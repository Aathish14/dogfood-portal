"""Public participation models - votes and comments (T3)."""
from sqlalchemy import String, Text, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone

from app.models.base import Base, TimestampMixin


class Vote(Base, TimestampMixin):
    __tablename__ = "votes"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    voter_fingerprint: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    value: Mapped[int] = mapped_column(default=1, nullable=False)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    event: Mapped["Event"] = relationship(back_populates="votes")
    project: Mapped["Project"] = relationship(back_populates="votes")
    user: Mapped[Optional["User"]] = relationship(back_populates="votes")
    
    __table_args__ = (
        UniqueConstraint("event_id", "project_id", "user_id", "voter_fingerprint", name="uq_vote_unique"),
        Index("ix_vote_event", "event_id"),
        Index("ix_vote_project", "project_id"),
    )


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_moderated: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    event: Mapped["Event"] = relationship(back_populates="comments")
    project: Mapped["Project"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")
    
    __table_args__ = (
        Index("ix_comment_event", "event_id"),
        Index("ix_comment_project", "project_id"),
        Index("ix_comment_author", "author_id"),
    )
