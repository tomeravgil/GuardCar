import asyncio
from core.services.sse.events.event_factory import SSEEventFactory
from core.services.sse.i_server_side_events_service import IServerSideEventsService


class ServerSideEventsService(IServerSideEventsService):

    def __init__(self, shutdown_event: asyncio.Event) -> None:
        self.shutdown_event = shutdown_event
        self.sse_queue = asyncio.Queue()

    def send_event(self, event: str, data: dict) -> None:
        # Implementation for sending a server-sent event
        event = SSEEventFactory.create_event(event, data)
        self.sse_queue.put_nowait(event)

    async def stream_events(self):
        try:
            while not self.shutdown_event.is_set():
                # Use asyncio.wait to listen for both queue and shutdown signals
                done, _ = await asyncio.wait(
                    [
                        self.sse_queue.get(),
                        self.shutdown_event.wait(),
                    ],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                # If shutdown event triggered, exit immediately
                if self.shutdown_event.is_set():
                    break

                # Get the completed task that’s not shutdown
                task = done.pop()
                event = task.result()
                yield event.to_sse_format()
                self.sse_queue.task_done()

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # This happens if the client disconnects or Uvicorn cancels the generator
            print("SSE stream cancelled (client disconnected or server shutting down).")
        finally:
            print("SSE stream exited cleanly.")

        