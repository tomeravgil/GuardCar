# api/routers/sse.py
from fastapi import APIRouter
from starlette.responses import StreamingResponse
from core.services.sse.server_side_events import ServerSideEventsService

router = APIRouter(prefix="/sse", tags=["sse"])

# This will be set during app bootstrap
sse_service: ServerSideEventsService | None = None

@router.get("/stream")
async def stream():
    assert sse_service is not None, "SSE service not initialized"
    return StreamingResponse(
        sse_service.stream_events(),
        media_type="text/event-stream",
        headers={
            # Helpful for proxies
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
