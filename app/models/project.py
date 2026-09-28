"""Project/Submission model."""
import enum
from sqlalchemy import String, Text, ForeignKey, Enum, Index, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone

from app.models.base import Base, TimestampMixin


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    LATE_REFUSED = "late_refused"
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"
    WITHDRAWN = "withdrawn"
    DUPLICATE = "duplicate"


class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    track_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tracks.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_duplicate: Mapped[bool] = mapped_column(default=False, nullable=False)
    duplicate_of_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    
    event: Mapped["Event"] = relationship(back_populates="projects")
    team: Mapped["Team"] = relationship(back_populates="projects")
    track: Mapped[Optional["Track"]] = relationship(back_populates="projects")
    judge_assignments: Mapped[List["JudgeAssignment"]] = relationship(back_populates="project")
    votes: Mapped[List["Vote"]] = relationship(back_populates="project")
    comments: Mapped[List["Comment"]] = relationship(back_populates="project")
    results: Mapped[List["Result"]] = relationship(back_populates="project")
    
    __table_args__ = (
        Index("ix_project_event", "event_id"),
        Index("ix_project_team", "team_id"),
        Index("ix_project_status", "status"),
        Index("ix_project_fixture", "is_fixture"),
    )
