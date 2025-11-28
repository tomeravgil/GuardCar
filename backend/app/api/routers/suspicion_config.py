from fastapi import APIRouter, Depends
from backend.app.core.use_cases.suspicion_config import SuspicionConfigurationUseCase, SuspicionConfigurationRequest
from backend.app.dependencies import get_suspicion_config_use_case

router = APIRouter(prefix="/api")

@router.post("/suspicion_config")
def register_provider(
        use_case: SuspicionConfigurationUseCase = Depends(get_suspicion_config_use_case),
        request: SuspicionConfigurationRequest=None
):
    return use_case.execute(request)