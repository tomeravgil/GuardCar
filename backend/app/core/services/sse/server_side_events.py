import asyncio
from core.services.sse.events.event_factory import SSEEventFactory
from core.services.sse.i_server_side_events_service import IServerSideEventsService


class ServerSideEventsService(IServerSideEventsService):

    sse_queue = asyncio.Queue()

    def send_event(self, event: str, data: dict) -> None:
        # Implementation for sending a server-sent event
        event = SSEEventFactory.create_event(event, data)
        self.sse_queue.put_nowait(event)

    async def stream_events(self):
        # Implementation for streaming server-sent events
        while True:
            event = await self.sse_queue.get()
            yield event.to_sse_format()
            await asyncio.sleep(0.1)
            self.sse_queue.task_done()