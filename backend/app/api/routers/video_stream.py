from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from backend.app.dependencies import get_video_stream_use_case
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["VideoWebSocket"])

@router.websocket("/video")
async def ws_video(ws: WebSocket):
    await ws.accept()

    video = get_video_stream_use_case()
    q = video.subscribe()

    selected = 0

    async def command_listener():
        nonlocal selected
        while True:
            try:
                msg = await ws.receive_json()
                if "camera" in msg:
                    selected = int(msg["camera"])
            except WebSocketDisconnect:
                break

    cmd_task = asyncio.create_task(command_listener())

    try:
        while True:
            jpeg = await q.get()

            if selected < 2:
                cam0, cam1 = video.split_frame(jpeg)
                img = cam0 if selected == 0 else cam1
                out = video.encode_jpeg(img)
            else:
                out = jpeg

            # If client disconnected, this will raise WebSocketDisconnect
            await ws.send_bytes(out)

    except WebSocketDisconnect:
        pass
    finally:
        cmd_task.cancel()
        video.unsubscribe(q)
