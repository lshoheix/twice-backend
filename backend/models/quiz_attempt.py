"""QuizAttempt model."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.account import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id: Mapped[str] = mapped_column(String(36), ForeignKey("accounts.id"), nullable=False)
    quiz_id: Mapped[str] = mapped_column(String(64), nullable=False)
    difficulty_level: Mapped[str] = mapped_column(String(16), nullable=False)  # LOW, MID, HIGH
    status: Mapped[str] = mapped_column(String(32), nullable=False)  # START, IN_PROGRESS, ABANDONED, FINISH
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    account: Mapped["Account"] = relationship("Account", back_populates="quiz_attempts")
