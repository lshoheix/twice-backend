"""Account model - UUID primary key."""
import uuid

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    kakao_id: Mapped[int | None] = mapped_column(nullable=True, unique=True)

    event_logs: Mapped[list["EventLog"]] = relationship("EventLog", back_populates="account")
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship("QuizAttempt", back_populates="account")
