"""Project schemas."""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    repo_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    track_id: Optional[int] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    repo_url: Optional[HttpUrl] = None
    demo_url: Optional[HttpUrl] = None
    video_url: Optional[HttpUrl] = None
    track_id: Optional[int] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    id: int
    event_id: int
    team_id: int
    track_id: Optional[int]
    status: ProjectStatus
    submitted_at: Optional[datetime]
    is_fixture: bool
    is_duplicate: bool
    duplicate_of_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectWithDetails(ProjectResponse):
    team_name: Optional[str] = None
    track_name: Optional[str] = None
    raw_aggregate: Optional[float] = None
    normalized_score: Optional[float] = None
    rank: Optional[int] = None
    vote_count: int = 0
