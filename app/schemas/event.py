"""Event schemas."""
from __future__ import annotations

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.event import EventStatus


class TrackResponse(BaseModel):
    id: int
    event_id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    is_fixture: bool

    class Config:
        from_attributes = True


class RubricResponse(BaseModel):
    id: int
    event_id: int
    version: int
    name: str
    description: Optional[str]
    is_frozen: bool
    is_fixture: bool
    criteria: List["CriterionResponse"] = []

    class Config:
        from_attributes = True


class CriterionResponse(BaseModel):
    id: int
    rubric_id: int
    label: str
    description: Optional[str]
    weight: float
    scale_min: int
    scale_max: int
    display_order: int
    is_fixture: bool

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    max_team_size: int = 4
    allow_late_submissions: bool = False


class EventCreate(EventBase):
    registration_open: Optional[datetime] = None
    registration_close: Optional[datetime] = None
    submissions_open: Optional[datetime] = None
    submissions_close: Optional[datetime] = None
    judging_open: Optional[datetime] = None
    judging_close: Optional[datetime] = None
    results_release: Optional[datetime] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[EventStatus] = None
    registration_open: Optional[datetime] = None
    registration_close: Optional[datetime] = None
    submissions_open: Optional[datetime] = None
    submissions_close: Optional[datetime] = None
    judging_open: Optional[datetime] = None
    judging_close: Optional[datetime] = None
    results_release: Optional[datetime] = None
    max_team_size: Optional[int] = None
    allow_late_submissions: Optional[bool] = None


class EventResponse(EventBase):
    id: int
    status: EventStatus
    registration_open: Optional[datetime]
    registration_close: Optional[datetime]
    submissions_open: Optional[datetime]
    submissions_close: Optional[datetime]
    judging_open: Optional[datetime]
    judging_close: Optional[datetime]
    results_release: Optional[datetime]
    is_fixture: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TrackResponse(BaseModel):
    id: int
    event_id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    is_fixture: bool

    class Config:
        from_attributes = True


class RubricResponse(BaseModel):
    id: int
    event_id: int
    version: int
    name: str
    description: Optional[str]
    is_frozen: bool
    is_fixture: bool
    criteria: List["CriterionResponse"] = []

    class Config:
        from_attributes = True


class CriterionResponse(BaseModel):
    id: int
    rubric_id: int
    label: str
    description: Optional[str]
    weight: float
    scale_min: int
    scale_max: int
    display_order: int
    is_fixture: bool

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    max_team_size: int = 4
    allow_late_submissions: bool = False


class EventCreate(EventBase):
    registration_open: Optional[datetime] = None
    registration_close: Optional[datetime] = None
    submissions_open: Optional[datetime] = None
    submissions_close: Optional[datetime] = None
    judging_open: Optional[datetime] = None
    judging_close: Optional[datetime] = None
    results_release: Optional[datetime] = None


class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[EventStatus] = None
    registration_open: Optional[datetime] = None
    registration_close: Optional[datetime] = None
    submissions_open: Optional[datetime] = None
    submissions_close: Optional[datetime] = None
    judging_open: Optional[datetime] = None
    judging_close: Optional[datetime] = None
    results_release: Optional[datetime] = None
    max_team_size: Optional[int] = None
    allow_late_submissions: Optional[bool] = None


class EventResponse(EventBase):
    id: int
    status: EventStatus
    registration_open: Optional[datetime]
    registration_close: Optional[datetime]
    submissions_open: Optional[datetime]
    submissions_close: Optional[datetime]
    judging_open: Optional[datetime]
    judging_close: Optional[datetime]
    results_release: Optional[datetime]
    is_fixture: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EventWithDetails(EventResponse):
    tracks: List[TrackResponse] = []
    rubrics: List["RubricResponse"] = []
    teams_count: int = 0
    projects_count: int = 0
    judges_count: int = 0
    participants_count: int = 0
