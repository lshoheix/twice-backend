"""Engagement 도메인 Service 인터페이스."""
from abc import ABC, abstractmethod
from engagement.models import ServiceAccessRequest, ServiceAccessResponse


class EngagementServiceInterface(ABC):
    """서비스 접속 기록 인터페이스."""

    @abstractmethod
    def record_access(self, request: ServiceAccessRequest) -> ServiceAccessResponse:
        """수강생의 서비스 접속을 기록한다 (MVP 1번)."""
        pass
