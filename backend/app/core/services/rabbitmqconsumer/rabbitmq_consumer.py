import asyncio
from dataclasses import asdict
from backend.app.core.services.sse.server_side_events import ServerSideEventsService
from rabbitMQ.dtos.dto import SuspicionFrameMessage, RecordingStatusMessage, ResponseMessage
import logging

logger = logging.getLogger(__name__)

class RabbitMQEventHandler:
    def __init__(
        self,
        event_queue: asyncio.Queue,
        server_side_event_service: ServerSideEventsService,
        shutdown_event: asyncio.Event | None = None
        ) -> None:
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event or asyncio.Event()
        self.sse_service = server_side_event_service

    async def run(self) -> None:
        while not self.shutdown_event.is_set():
            msg = await self.event_queue.get()
            self._handle_event(msg)
            self.event_queue.task_done()

    def _handle_event(self, msg):
        try:
            if isinstance(msg,SuspicionFrameMessage):
                self.sse_service.send_event("suspicion",asdict(msg))
            elif isinstance(msg,RecordingStatusMessage):
                self.sse_service.send_event("recording",asdict(msg))
            elif isinstance(msg,ResponseMessage):
                if msg.success:
                    self.sse_service.send_event("success",asdict(msg))
                else:
                    self.sse_service.send_event("failure",asdict(msg))
        except Exception as e:
            logger.error(e)

