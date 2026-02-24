"""Aggregation 도메인 Controller. 참여율/4주 지속률 API."""
from fastapi import APIRouter, Depends
from .models import ParticipationRateResponse, Retention4WeeksResponse
from .service_interface import AggregationServiceInterface

router = APIRouter()


def get_aggregation_service() -> AggregationServiceInterface:
    """DI: main에서 구현체로 override."""
    raise NotImplementedError("main에서 구현체를 주입해 주세요.")


@router.get(
    "/participation-rate",
    response_model=ParticipationRateResponse,
    summary="참여율",
    description="MVP 9: 참여율을 계산하여 반환합니다.",
)
def get_participation_rate(
    service: AggregationServiceInterface = Depends(get_aggregation_service),
) -> ParticipationRateResponse:
    return service.get_participation_rate()


@router.get(
    "/retention-4weeks",
    response_model=Retention4WeeksResponse,
    summary="4주 지속률",
    description="MVP 9: 4주 지속률을 계산하여 반환합니다.",
)
def get_retention_4weeks(
    service: AggregationServiceInterface = Depends(get_aggregation_service),
) -> Retention4WeeksResponse:
    return service.get_retention_4weeks()
