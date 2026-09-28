"""Event model."""
import enum
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone

from app.models.base import Base, TimestampMixin


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    REGISTRATION = "registration"
    SUBMISSIONS = "submissions"
    JUDGING = "judging"
    RESULTS_LOCKED = "results_locked"
    PUBLISHED = "published"


class Event(Base, TimestampMixin):
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), default=EventStatus.DRAFT, nullable=False)
    
    registration_open: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    registration_close: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submissions_open: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submissions_close: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    judging_open: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    judging_close: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    results_release: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    max_team_size: Mapped[int] = mapped_column(default=4, nullable=False)
    allow_late_submissions: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    role_memberships: Mapped[List["RoleMembership"]] = relationship(back_populates="event")
    teams: Mapped[List["Team"]] = relationship(back_populates="event")
    tracks: Mapped[List["Track"]] = relationship(back_populates="event")
    projects: Mapped[List["Project"]] = relationship(back_populates="event")
    rubrics: Mapped[List["Rubric"]] = relationship(back_populates="event")
    judge_assignments: Mapped[List["JudgeAssignment"]] = relationship(back_populates="event")
    review_batches: Mapped[List["ReviewBatch"]] = relationship(back_populates="event")
    normalization_runs: Mapped[List["NormalizationRun"]] = relationship(back_populates="event")
    votes: Mapped[List["Vote"]] = relationship(back_populates="event")
    comments: Mapped[List["Comment"]] = relationship(back_populates="event")
    audit_events: Mapped[List["AuditEvent"]] = relationship(back_populates="event")
    webhook_subscriptions: Mapped[List["WebhookSubscription"]] = relationship(back_populates="event")
    
    __table_args__ = (
        Index("ix_event_status", "status"),
        Index("ix_event_fixture", "is_fixture"),
    )
