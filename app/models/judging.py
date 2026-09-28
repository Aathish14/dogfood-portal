"""Judging models - assignments, batches, reviews, scores."""
import enum
from sqlalchemy import String, Text, ForeignKey, Enum, DateTime, Integer, Numeric, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone

from app.models.base import Base, TimestampMixin


class AssignmentStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REASSIGNED = "reassigned"


class ReviewStatus(str, enum.Enum):
    UNSTARTED = "unstarted"
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REOPENED = "reopened"
    VOIDED = "voided"


class JudgeAssignment(Base, TimestampMixin):
    __tablename__ = "judge_assignments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    judge_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    batch_id: Mapped[Optional[int]] = mapped_column(ForeignKey("review_batches.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[AssignmentStatus] = mapped_column(Enum(AssignmentStatus), default=AssignmentStatus.ASSIGNED, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    event: Mapped["Event"] = relationship(back_populates="judge_assignments")
    judge: Mapped["User"] = relationship(back_populates="judge_assignments")
    project: Mapped["Project"] = relationship(back_populates="judge_assignments")
    batch: Mapped[Optional["ReviewBatch"]] = relationship(back_populates="assignments")
    review: Mapped[Optional["Review"]] = relationship(back_populates="assignment")
    
    __table_args__ = (
        UniqueConstraint("judge_id", "project_id", "event_id", name="uq_judge_project_event"),
        Index("ix_judge_assignment_judge", "judge_id"),
        Index("ix_judge_assignment_project", "project_id"),
        Index("ix_judge_assignment_batch", "batch_id"),
        Index("ix_judge_assignment_status", "status"),
    )


class ReviewBatch(Base, TimestampMixin):
    __tablename__ = "review_batches"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    event: Mapped["Event"] = relationship(back_populates="review_batches")
    assignments: Mapped[List["JudgeAssignment"]] = relationship(back_populates="batch")
    
    __table_args__ = (
        Index("ix_review_batch_event", "event_id"),
    )


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("judge_assignments.id", ondelete="CASCADE"), nullable=False)
    judge_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.UNSTARTED, nullable=False)
    general_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    assignment: Mapped["JudgeAssignment"] = relationship(back_populates="review")
    judge: Mapped["User"] = relationship(back_populates="reviews")
    scores: Mapped[List["Score"]] = relationship(back_populates="review", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("assignment_id", name="uq_review_assignment"),
        Index("ix_review_judge", "judge_id"),
        Index("ix_review_status", "status"),
    )


class Score(Base, TimestampMixin):
    __tablename__ = "scores"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    review_id: Mapped[int] = mapped_column(ForeignKey("reviews.id", ondelete="CASCADE"), nullable=False)
    criterion_id: Mapped[int] = mapped_column(ForeignKey("criteria.id", ondelete="CASCADE"), nullable=False)
    value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    review: Mapped["Review"] = relationship(back_populates="scores")
    criterion: Mapped["Criterion"] = relationship(back_populates="scores")
    
    __table_args__ = (
        UniqueConstraint("review_id", "criterion_id", name="uq_score_review_criterion"),
        Index("ix_score_review", "review_id"),
        Index("ix_score_criterion", "criterion_id"),
    )
