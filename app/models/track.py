"""Track model."""
from sqlalchemy import String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.models.base import Base, TimestampMixin


class Track(Base, TimestampMixin):
    __tablename__ = "tracks"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    is_fixture: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    event: Mapped["Event"] = relationship(back_populates="tracks")
    projects: Mapped[List["Project"]] = relationship(back_populates="track")
    
    __table_args__ = (
        Index("ix_track_event", "event_id"),
    )
