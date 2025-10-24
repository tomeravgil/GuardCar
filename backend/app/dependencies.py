from core.use_cases.evaluate_suspicion import EvaluateSuspicionUseCase
from api.schemas.thresholds import UIThresholds
from core.services.suspicion.i_suspicion_service import ISuspicionService, SuspicionService
from core.services.sse.i_server_side_events_service import IServerSideEventsService
from core.use_cases.sse_connection import ServerSideEventsUseCase
from core.services.sse.server_side_events import ServerSideEventsService

ui_thresholds = UIThresholds(suspicion_score_threshold=70)
_suspicion_service = SuspicionService()
_sse_service = ServerSideEventsService()

def get_suspicion_service() -> ISuspicionService:
    return _suspicion_service

def get_sse_service() -> IServerSideEventsService:
    return _sse_service

def get_suspicion_use_case():
    suspicion_service = get_suspicion_service()
    sse_service = get_sse_service()

    return EvaluateSuspicionUseCase(
        suspicion_service=suspicion_service,
        sse_service=sse_service,
        threshold=ui_thresholds.suspicion_score_threshold)

def get_sse_use_case():
    sse_service = get_sse_service()

    return ServerSideEventsUseCase(sse_service=sse_service)