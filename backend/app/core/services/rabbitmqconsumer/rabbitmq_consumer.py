# core/services/rabbitmq_consumer.py
import asyncio
import json
import aio_pika
from typing import Callable, Awaitable

OnMessage = Callable[[dict], Awaitable[None]]

class RabbitMQConsumer:
    def __init__(
        self,
        amqp_url: str,
        queue_name: str,
        on_message: OnMessage,
        *,
        prefetch: int = 32,
        shutdown_event: asyncio.Event | None = None,
    ) -> None:
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self.on_message = on_message
        self.prefetch = prefetch
        self.shutdown_event = shutdown_event or asyncio.Event()

    async def run(self) -> None:
        backoff = 1
        while not self.shutdown_event.is_set():
            try:
                conn = await aio_pika.connect_robust(self.amqp_url)
                async with conn:
                    ch = await conn.channel()
                    await ch.set_qos(prefetch_count=self.prefetch)
                    q = await ch.declare_queue(self.queue_name, durable=True)

                    async with q.iterator() as qiter:
                        async for msg in qiter:
                            if self.shutdown_event.is_set():
                                break
                            async with msg.process(requeue=False):
                                try:
                                    payload = json.loads(msg.body.decode("utf-8"))
                                except Exception:
                                    payload = {"raw": msg.body.decode("utf-8", "ignore")}
                                await self.on_message(payload)
                backoff = 1  # reset after a clean exit
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(min(backoff, 10))
                backoff = min(backoff * 2, 10)
