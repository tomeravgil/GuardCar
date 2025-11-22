# core/services/sse/server_side_events.py

import asyncio
from .events.event_factory import SSEEventFactory
from .i_server_side_events_service import IServerSideEventsService


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
                
                # Create tasks for both the queue get and shutdown event
                queue_task = asyncio.create_task(self.sse_queue.get())
                shutdown_task = asyncio.create_task(self.shutdown_event.wait())
                
                # Use asyncio.wait to listen for both queue and shutdown signals
                done, pending = await asyncio.wait(
                    [queue_task, shutdown_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # Cancel pending tasks to avoid them running in the background
                for task in pending:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

                # If shutdown event triggered, exit immediately
                if self.shutdown_event.is_set():
                    break

                # Get the completed task that's not shutdown
                task = done.pop()
                if task == queue_task:
                    event = task.result()
                    yield event.to_sse_format()
                    self.sse_queue.task_done()

                # Small pause is optional; can be removed
                # await asyncio.sleep(0)  # cooperative yield
        except asyncio.CancelledError:
            # Client disconnected or server shutdown
            print("SSE stream cancelled.")
        finally:
            print("SSE stream exited cleanly.")

