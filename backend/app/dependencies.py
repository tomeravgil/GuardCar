from app.core.use_cases.evaluate_suspicion import EvaluateSuspicionUseCase
from app.api.schemas.thresholds import UIThresholds
from app.core.services.suspicion.i_suspicion_service import ISuspicionService, SuspicionService

ui_thresholds = UIThresholds(suspicion_score_threshold=70)
_suspicion_service = SuspicionService()

def get_suspicion_service() -> ISuspicionService:
    return _suspicion_service

def get_suspicion_use_case():
    suspicion_service = get_suspicion_service()

    return EvaluateSuspicionUseCase(
        suspicion_service=suspicion_service,
        threshold=ui_thresholds.suspicion_score_threshold)
