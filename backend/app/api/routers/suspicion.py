from fastapi import APIRouter, Body, Depends
from api.schemas.yolo_input import YoloInput
from api.schemas.responses import SuspicionResponse, VideoResponse
from core.use_cases.evaluate_suspicion import EvaluateSuspicionUseCase
from dependencies import get_suspicion_use_case

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
