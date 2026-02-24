"""Quiz 도메인 Service 구현체. Mock 데이터 사용."""
import uuid
from datetime import datetime, timedelta
from .models import (
    QuizState,
    QuizStartRequest,
    QuizStartResponse,
    QuizFinishRequest,
    QuizFinishResponse,
)
from .service_interface import QuizServiceInterface

# Mock: 퀴즈 세션 — 30명 (user-01 ~ user-30). 약 20명 완료(finish), 10명 중도포기(start만)
def _build_mock_sessions() -> list[dict]:
    now = datetime.utcnow()
    out = []
    evaluations = ("Good", "Fair", "Excellent", "Need practice", "Well done")
    for i in range(1, 31):
        user_id = f"user-{i:02d}"
        started_at = now - timedelta(days=i % 7, hours=24 - i)
        # user-01~20: 완료, user-21~30: 시작만 (중도포기)
        if i <= 20:
            finished_at = started_at + timedelta(minutes=5 + (i % 15))
            score = 55.0 + (i * 1.5) + (i % 10)  # 60~90대 분산
            if score > 100:
                score = 95.0
            out.append({
                "session_id": f"sess-{i:03d}",
                "user_id": user_id,
                "quiz_id": "quiz-1",
                "state": QuizState.FINISH,
                "started_at": started_at,
                "finished_at": finished_at,
                "score": round(score, 1),
                "improvement_rate": round(5 + i % 15, 1),
                "evaluation": evaluations[i % len(evaluations)],
            })
        else:
            out.append({
                "session_id": f"sess-{i:03d}",
                "user_id": user_id,
                "quiz_id": "quiz-1",
                "state": QuizState.START,
                "started_at": started_at,
                "finished_at": None,
                "score": None,
                "improvement_rate": None,
                "evaluation": None,
            })
    return out


_MOCK_SESSIONS = _build_mock_sessions()


class QuizServiceImpl(QuizServiceInterface):
    """퀴즈 상태/점수 저장 구현체 (Mock)."""

    def __init__(self) -> None:
        self._sessions: list[dict] = [self._copy_sess(s) for s in _MOCK_SESSIONS]

    @staticmethod
    def _copy_sess(s: dict) -> dict:
        return dict(s)

    def start_quiz(self, request: QuizStartRequest) -> QuizStartResponse:
        started_at = datetime.utcnow()
        session_id = f"sess-{uuid.uuid4().hex[:8]}"
        self._sessions.append({
            "session_id": session_id,
            "user_id": request.user_id,
            "quiz_id": request.quiz_id,
            "state": QuizState.START,
            "started_at": started_at,
            "finished_at": None,
            "score": None,
            "improvement_rate": None,
            "evaluation": None,
        })
        return QuizStartResponse(
            session_id=session_id,
            user_id=request.user_id,
            quiz_id=request.quiz_id,
            state=QuizState.START,
            started_at=started_at,
        )

    def finish_quiz(self, request: QuizFinishRequest) -> QuizFinishResponse:
        finished_at = datetime.utcnow()
        session = None
        for s in self._sessions:
            if s["session_id"] == request.session_id and s["state"] == QuizState.START:
                session = s
                break
        if not session:
            raise ValueError(f"해당 세션을 찾을 수 없거나 이미 완료되었습니다: {request.session_id}")
        session["state"] = QuizState.FINISH
        session["finished_at"] = finished_at
        session["score"] = request.score
        session["improvement_rate"] = request.improvement_rate
        session["evaluation"] = request.evaluation
        return QuizFinishResponse(
            session_id=session["session_id"],
            user_id=session["user_id"],
            quiz_id=session["quiz_id"],
            state=QuizState.FINISH,
            started_at=session["started_at"],
            finished_at=finished_at,
            score=request.score,
            improvement_rate=request.improvement_rate,
            evaluation=request.evaluation,
        )

    def get_all_sessions(self) -> list[dict]:
        """Aggregation 등에서 참여율/지속률 계산용 (Mock)."""
        return list(self._sessions)
