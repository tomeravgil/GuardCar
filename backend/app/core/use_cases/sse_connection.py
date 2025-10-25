from core.services.sse.i_server_side_events_service import IServerSideEventsService
from fastapi.responses import StreamingResponse

class ServerSideEventsUseCase:

    def __init__(self, sse_service: IServerSideEventsService):
        self.sse_service = sse_service

    def execute(self):
        # Example event data
        return StreamingResponse(self.sse_service.stream_events(), media_type="text/event-stream")
