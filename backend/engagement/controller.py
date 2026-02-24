"""Engagement 도메인 Controller. 서비스 접속 기록 API."""
from fastapi import APIRouter, Depends
from .models import ServiceAccessRequest, ServiceAccessResponse
from .service_interface import EngagementServiceInterface

router = APIRouter()


def get_engagement_service() -> EngagementServiceInterface:
    """DI: main에서 구현체로 override."""
    raise NotImplementedError("main에서 구현체를 주입해 주세요.")


@router.post(
    "/access",
    response_model=ServiceAccessResponse,
    summary="서비스 접속 기록",
    description="MVP 1: 수강생이 서비스에 접속했을 때 기록합니다.",
)
def record_access(
    body: ServiceAccessRequest,
    service: EngagementServiceInterface = Depends(get_engagement_service),
) -> ServiceAccessResponse:
    return service.record_access(body)
