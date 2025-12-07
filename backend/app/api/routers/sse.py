from fastapi import APIRouter, Depends
from backend.app.core.use_cases.sse_connection import ServerSideEventsUseCase
from backend.app.dependencies import get_sse_use_case

router = APIRouter(prefix="/api")

@router.get("/sse", response_model=None)
def sse_endpoint(
    use_case: ServerSideEventsUseCase = Depends(get_sse_use_case)
):
    return use_case.execute()