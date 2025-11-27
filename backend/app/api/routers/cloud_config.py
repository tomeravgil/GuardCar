from fastapi import APIRouter, Depends
from backend.app.core.use_cases.cloud_config import (CloudConfigurationConfigurationUseCase,
                                                     CloudConfigurationRequest, \
                                                     CloudConfigurationDeleteRequest)
from backend.app.dependencies import get_cloud_provider_config_use_case

router = APIRouter(prefix="/api")

@router.post("/register_provider")
def register_provider(
        use_case: CloudConfigurationConfigurationUseCase = Depends(get_cloud_provider_config_use_case),
        request: CloudConfigurationRequest=None
):
    return use_case.create(request)


@router.delete("/delete_provider")
def delete_provider(
        use_case: CloudConfigurationConfigurationUseCase = Depends(get_cloud_provider_config_use_case),
        request: CloudConfigurationDeleteRequest=None
):
    return use_case.delete(request)