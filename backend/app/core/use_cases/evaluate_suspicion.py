from app.core.entities.suspicion import SuspicionLevel
from app.core.services.suspicion.i_suspicion_service import ISuspicionService

class EvaluateSuspicionUseCase:
    def __init__(self, 
                suspicion_service: ISuspicionService,
                 threshold: int):
        self.threshold = threshold
        self.suspicion_service = suspicion_service

    def execute(self, score: int) -> SuspicionLevel:
        suspicion_level = self.suspicion_service.evaluate(score)
        return suspicion_level
