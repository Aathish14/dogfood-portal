"""Team schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class TeamMemberResponse(BaseModel):
    user_id: int
    username: str
    display_name: str
    email: Optional[str]
    is_leader: bool

    class Config:
        from_attributes = True


class TeamResponse(TeamBase):
    id: int
    event_id: int
    is_fixture: bool
    created_at: datetime
    updated_at: datetime
    members: List[TeamMemberResponse] = []

    class Config:
        from_attributes = True


class JoinTeamRequest(BaseModel):
    team_id: int
