"""Role and role membership models."""
import enum
from sqlalchemy import String, ForeignKey, Enum, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.models.base import Base, TimestampMixin


class Role(str, enum.Enum):
    ORGANIZER = "organizer"
    JUDGE = "judge"
    PARTICIPANT = "participant"


class RoleMembership(Base, TimestampMixin):
    __tablename__ = "role_memberships"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    
    user: Mapped["User"] = relationship(back_populates="role_memberships")
    event: Mapped["Event"] = relationship(back_populates="role_memberships")
    
    __table_args__ = (
        UniqueConstraint("user_id", "event_id", "role", name="uq_user_event_role"),
        Index("ix_role_membership_user_event", "user_id", "event_id"),
    )
