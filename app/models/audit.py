"""Audit and webhook models."""
from sqlalchemy import String, Text, ForeignKey, DateTime, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone

from app.models.base import Base, TimestampMixin


class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    actor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    actor_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_id: Mapped[Optional[int]] = mapped_column(nullable=True)
    outcome: Mapped[str] = mapped_column(String(50), nullable=False)
    meta: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    event: Mapped[Optional["Event"]] = relationship(back_populates="audit_events")
    actor: Mapped[Optional["User"]] = relationship(back_populates="audit_events")
    
    __table_args__ = (
        Index("ix_audit_event_event", "event_id"),
        Index("ix_audit_event_actor", "actor_id"),
        Index("ix_audit_event_timestamp", "timestamp"),
        Index("ix_audit_event_action", "action"),
    )


class WebhookSubscription(Base, TimestampMixin):
    __tablename__ = "webhook_subscriptions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    event_types: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    event: Mapped["Event"] = relationship(back_populates="webhook_subscriptions")
    deliveries: Mapped[List["WebhookDelivery"]] = relationship(back_populates="subscription")
    
    __table_args__ = (
        Index("ix_webhook_subscription_event", "event_id"),
    )


class WebhookDelivery(Base, TimestampMixin):
    __tablename__ = "webhook_deliveries"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    response_status: Mapped[Optional[int]] = mapped_column(nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attempt: Mapped[int] = mapped_column(default=1, nullable=False)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    subscription: Mapped["WebhookSubscription"] = relationship(back_populates="deliveries")
    
    __table_args__ = (
        Index("ix_webhook_delivery_subscription", "subscription_id"),
        Index("ix_webhook_delivery_status", "response_status"),
    )
