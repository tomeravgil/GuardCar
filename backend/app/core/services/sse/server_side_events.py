# core/services/sse/server_side_events.py

import asyncio
from core.services.sse.events.event_factory import SSEEventFactory
from core.services.sse.i_server_side_events_service import IServerSideEventsService


class ServerSideEventsService(IServerSideEventsService):
    def __init__(self, shutdown_event: asyncio.Event) -> None:
        self.shutdown_event = shutdown_event
        # Consider a bounded queue to apply backpressure if producers get ahead
        self.sse_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

    def send_event(self, event: str, data: dict) -> None:
        evt = SSEEventFactory.create_event(event, data)
        # put_nowait is fine here—if you want safety, catch QueueFull and drop/aggregate
        self.sse_queue.put_nowait(evt)

    async def stream_events(self):
        """
        Async generator for SSE. Yields lines formatted by your event's `to_sse_format()`.
        - Properly wraps coroutines in Tasks for asyncio.wait
        - Cancels the losing task each loop to avoid leaks
        - Exits quickly on shutdown
        """
        try:
            # Optional: emit a quick "hello" to confirm stream is alive
            self.send_event("hello", {"msg": "connected"})

            while not self.shutdown_event.is_set():
                get_task = asyncio.create_task(self.sse_queue.get())
                stop_task = asyncio.create_task(self.shutdown_event.wait())

                done, pending = await asyncio.wait(
                    {get_task, stop_task},
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Always cancel the task that didn't finish
                for p in pending:
                    p.cancel()

                # If shutdown fired, exit immediately
                if stop_task in done and self.shutdown_event.is_set():
                    break

                # A queue item is ready
                if get_task in done:
                    event = get_task.result()
                    # Yield one SSE event (already formatted by your event type)
                    yield event.to_sse_format()
                    self.sse_queue.task_done()

                # Small pause is optional; can be removed
                # await asyncio.sleep(0)  # cooperative yield
        except asyncio.CancelledError:
            # Client disconnected or server shutdown
            print("SSE stream cancelled.")
        finally:
            print("SSE stream exited cleanly.")
