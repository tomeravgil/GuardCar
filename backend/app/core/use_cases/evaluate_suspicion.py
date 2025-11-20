from app.core.entities.suspicion import SuspicionLevel
from app.core.services.suspicion.i_suspicion_service import ISuspicionService
from app.core.services.sse.i_server_side_events_service import IServerSideEventsService

class EvaluateSuspicionUseCase:
    def __init__(self, 
                suspicion_service: ISuspicionService,
                sse_service: IServerSideEventsService,
                 threshold: int):
        self.threshold = threshold
        self.suspicion_service = suspicion_service
        self.sse_service = sse_service

    def execute(self, score: int) -> SuspicionLevel:
        suspicion_level = self.suspicion_service.evaluate(score)
        self.sse_service.send_event("event", {"level": suspicion_level.level})
        return suspicion_level
