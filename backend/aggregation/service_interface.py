"""Aggregation 도메인 Service 인터페이스."""
from abc import ABC, abstractmethod
from .models import ParticipationRateResponse, Retention4WeeksResponse


class AggregationServiceInterface(ABC):
    """참여율/4주 지속률 계산 인터페이스."""

    @abstractmethod
    def get_participation_rate(self) -> ParticipationRateResponse:
        """참여율을 계산한다 (MVP 9)."""
        pass

    @abstractmethod
    def get_retention_4weeks(self) -> Retention4WeeksResponse:
        """4주 지속률을 계산한다 (MVP 9)."""
        pass
