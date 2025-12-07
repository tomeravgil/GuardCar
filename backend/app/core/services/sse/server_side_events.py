import asyncio
from backend.app.core.services.sse.events.event_factory import SSEEventFactory
from backend.app.core.services.sse.i_server_side_events_service import IServerSideEventsService

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
                queue_task = asyncio.create_task(self.sse_queue.get())
                shutdown_task = asyncio.create_task(self.shutdown_event.wait())

                done, pending = await asyncio.wait(
                    [queue_task, shutdown_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for task in pending:
                    task.cancel()

                if self.shutdown_event.is_set():
                    break

                if queue_task in done:
                    event = queue_task.result()
                    yield event.to_sse_format()
                    self.sse_queue.task_done()

                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            # This happens if the client disconnects or Uvicorn cancels the generator
            print("SSE stream cancelled (client disconnected or server shutting down).")
        finally:
            print("SSE stream exited cleanly.")

