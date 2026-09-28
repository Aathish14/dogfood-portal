"""Rubric and criterion models."""
from sqlalchemy import String, Text, ForeignKey, Numeric, Integer, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.models.base import Base, TimestampMixin


class Rubric(Base, TimestampMixin):
    __tablename__ = "rubrics"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_frozen: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    event: Mapped["Event"] = relationship(back_populates="rubrics")
    criteria: Mapped[List["Criterion"]] = relationship(back_populates="rubric")
    
    __table_args__ = (
        Index("ix_rubric_event", "event_id"),
        UniqueConstraint("event_id", "version", name="uq_rubric_event_version"),
    )


class Criterion(Base, TimestampMixin):
    __tablename__ = "criteria"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rubric_id: Mapped[int] = mapped_column(ForeignKey("rubrics.id", ondelete="CASCADE"), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    scale_min: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scale_max: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    rubric: Mapped["Rubric"] = relationship(back_populates="criteria")
    scores: Mapped[List["Score"]] = relationship(back_populates="criterion")
    
    __table_args__ = (
        Index("ix_criterion_rubric", "rubric_id"),
    )
