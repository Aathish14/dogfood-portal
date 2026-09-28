"""Result and normalization models."""
import enum
from sqlalchemy import String, Text, ForeignKey, Enum, DateTime, Numeric, Integer, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import datetime, timezone

from app.models.base import Base, TimestampMixin


class NormalizationMethod(str, enum.Enum):
    Z_SCORE = "z_score"
    ROBUST_Z_SCORE = "robust_z_score"
    PERCENTILE = "percentile"
    RAW_AVERAGE = "raw_average"
    BRADLEY_TERRY = "bradley_terry"


class NormalizationRun(Base, TimestampMixin):
    __tablename__ = "normalization_runs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    rubric_id: Mapped[int] = mapped_column(ForeignKey("rubrics.id", ondelete="CASCADE"), nullable=False)
    method: Mapped[NormalizationMethod] = mapped_column(Enum(NormalizationMethod), nullable=False)
    parameters: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    initiated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    warnings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    event: Mapped["Event"] = relationship(back_populates="normalization_runs")
    rubric: Mapped["Rubric"] = relationship()
    initiator: Mapped["User"] = relationship()
    results: Mapped[List["Result"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_normalization_run_event", "event_id"),
        Index("ix_normalization_run_published", "is_published"),
    )


class Result(Base, TimestampMixin):
    __tablename__ = "results"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("normalization_runs.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    raw_aggregate: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), nullable=True)
    normalized_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 4), nullable=True)
    rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tie_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    criterion_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    run: Mapped["NormalizationRun"] = relationship(back_populates="results")
    project: Mapped["Project"] = relationship(back_populates="results")
    
    __table_args__ = (
        UniqueConstraint("run_id", "project_id", name="uq_result_run_project"),
        Index("ix_result_run", "run_id"),
        Index("ix_result_rank", "rank"),
    )
