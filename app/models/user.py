"""User model."""
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_fixture: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    role_memberships: Mapped[List["RoleMembership"]] = relationship(back_populates="user")
    team_memberships: Mapped[List["TeamMember"]] = relationship(back_populates="user")
    judge_assignments: Mapped[List["JudgeAssignment"]] = relationship(back_populates="judge")
    reviews: Mapped[List["Review"]] = relationship(back_populates="judge")
    votes: Mapped[List["Vote"]] = relationship(back_populates="user")
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")
    audit_events: Mapped[List["AuditEvent"]] = relationship(back_populates="actor")
