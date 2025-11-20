from fastapi import APIRouter, Body, Depends
from app.api.schemas.yolo_input import YoloInput
from app.api.schemas.responses import SuspicionResponse, VideoResponse
from app.core.use_cases.evaluate_suspicion import EvaluateSuspicionUseCase
from app.dependencies import get_suspicion_use_case

router = APIRouter(prefix="/api")

@router.post("/suspicionResult", response_model=SuspicionResponse)
def suspicion_result(
    payload: YoloInput = Body(..., embed=False),
    use_case: EvaluateSuspicionUseCase = Depends(get_suspicion_use_case)
):
    result = use_case.execute(payload.suspicion_score)
    return SuspicionResponse(message=result.message)

@router.post("/videoResult", response_model=VideoResponse)
def video_result(payload: YoloInput = Body(..., embed=False)):
    return VideoResponse(message="This is a Video")
