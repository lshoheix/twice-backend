"""Quiz 도메인 Controller. 퀴즈 시작/완료 API."""
from fastapi import APIRouter, Depends, HTTPException
from .models import QuizStartRequest, QuizStartResponse, QuizFinishRequest, QuizFinishResponse
from .service_interface import QuizServiceInterface

router = APIRouter()


def get_quiz_service() -> QuizServiceInterface:
    """DI: main에서 구현체로 override."""
    raise NotImplementedError("main에서 구현체를 주입해 주세요.")


@router.post(
    "/start",
    response_model=QuizStartResponse,
    summary="퀴즈 시작",
    description="MVP 2: 수강생이 퀴즈를 시작합니다. 상태는 start로 저장됩니다.",
)
def start_quiz(
    body: QuizStartRequest,
    service: QuizServiceInterface = Depends(get_quiz_service),
) -> QuizStartResponse:
    return service.start_quiz(body)


@router.post(
    "/finish",
    response_model=QuizFinishResponse,
    summary="퀴즈 완료",
    description="MVP 4~6: 퀴즈 완료 시 상태를 finish로 저장하고 점수(개선율, Evaluation)를 저장합니다.",
)
def finish_quiz(
    body: QuizFinishRequest,
    service: QuizServiceInterface = Depends(get_quiz_service),
) -> QuizFinishResponse:
    try:
        return service.finish_quiz(body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
