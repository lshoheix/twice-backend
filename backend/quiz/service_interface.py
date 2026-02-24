"""Quiz 도메인 Service 인터페이스."""
from abc import ABC, abstractmethod
from .models import (
    QuizState,
    QuizStartRequest,
    QuizStartResponse,
    QuizFinishRequest,
    QuizFinishResponse,
)


class QuizServiceInterface(ABC):
    """퀴즈 상태/점수 저장 인터페이스."""

    @abstractmethod
    def start_quiz(self, request: QuizStartRequest) -> QuizStartResponse:
        """퀴즈 시작. 상태를 start로 저장 (MVP 2)."""
        pass

    @abstractmethod
    def finish_quiz(self, request: QuizFinishRequest) -> QuizFinishResponse:
        """퀴즈 완료. 상태를 finish로 저장하고 점수 저장 (MVP 4~6)."""
        pass
