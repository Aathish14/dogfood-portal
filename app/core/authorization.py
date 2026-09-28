"""Centralized backend authorization."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import RoleMembership, Role
from app.models.event import Event
from app.models.team import Team, TeamMember
from app.models.project import Project
from app.models.judging import JudgeAssignment, Review, Score
from app.core.auth import AuthService


class AuthorizationError(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_403_FORBIDDEN):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class Authz:
    def __init__(self, db: Session, current_user: User = None, current_event_id: Optional[int] = None):
        self.db = db
        self.current_user = current_user
        self.current_event_id = current_event_id
        self.auth_service = AuthService(db)
    
    def require_authenticated(self) -> User:
        if not self.current_user:
            raise AuthorizationError("Authentication required", status.HTTP_401_UNAUTHORIZED)
        return self.current_user
    
    def require_role(self, role: Role, event_id: Optional[int] = None) -> User:
        user = self.require_authenticated()
        eid = event_id or self.current_event_id
        if not eid:
            raise AuthorizationError("Event context required", status.HTTP_403_FORBIDDEN)
        if not self.auth_service.has_role(user.id, eid, role):
            raise AuthorizationError(f"Role {role.value} required", status.HTTP_403_FORBIDDEN)
        return user
    
    def require_organizer(self, event_id: Optional[int] = None) -> User:
        return self.require_role(Role.ORGANIZER, event_id)
    
    def require_judge(self, event_id: Optional[int] = None) -> User:
        return self.require_role(Role.JUDGE, event_id)
    
    def require_participant(self, event_id: Optional[int] = None) -> User:
        return self.require_role(Role.PARTICIPANT, event_id)
    
    def can_access_judge_scores(self, target_judge_id: int, event_id: Optional[int] = None) -> bool:
        user = self.require_authenticated()
        eid = event_id or self.current_event_id
        
        if self.auth_service.has_role(user.id, eid, Role.ORGANIZER):
            return True
        if self.auth_service.has_role(user.id, eid, Role.JUDGE):
            return user.id == target_judge_id
        return False
    
    def require_judge_score_access(self, target_judge_id: int, event_id: Optional[int] = None) -> User:
        user = self.require_authenticated()
        eid = event_id or self.current_event_id
        
        if self.auth_service.has_role(user.id, eid, Role.ORGANIZER):
            return user
        
        if self.auth_service.has_role(user.id, eid, Role.JUDGE):
            if user.id == target_judge_id:
                return user
            raise AuthorizationError("Cannot access another judge's scores", status.HTTP_403_FORBIDDEN)
        
        raise AuthorizationError("Access denied", status.HTTP_403_FORBIDDEN)
    
    def can_manage_event(self, event_id: int) -> bool:
        user = self.require_authenticated()
        return self.auth_service.has_role(user.id, event_id, Role.ORGANIZER)
    
    def can_submit_project(self, team_id: int, event_id: int) -> bool:
        user = self.require_authenticated()
        if not self.auth_service.has_role(user.id, event_id, Role.PARTICIPANT):
            return False
        membership = self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user.id
            )
        ).scalar_one_or_none()
        return membership is not None
    
    def can_view_project(self, project_id: int) -> bool:
        return True
    
    def can_access_team(self, team_id: int, event_id: int) -> bool:
        user = self.require_authenticated()
        if self.auth_service.has_role(user.id, event_id, Role.ORGANIZER):
            return True
        membership = self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user.id
            )
        ).scalar_one_or_none()
        return membership is not None
    
    def require_team_access(self, team_id: int, event_id: int) -> User:
        user = self.require_authenticated()
        if self.auth_service.has_role(user.id, event_id, Role.ORGANIZER):
            return user
        membership = self.db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user.id
            )
        ).scalar_one_or_none()
        if not membership:
            raise AuthorizationError("Not a member of this team", status.HTTP_403_FORBIDDEN)
        return user
    
    def can_judge_project(self, project_id: int, event_id: int) -> bool:
        user = self.require_authenticated()
        eid = event_id or self.current_event_id
        if not self.auth_service.has_role(user.id, eid, Role.JUDGE):
            return False
        assignment = self.db.execute(
            select(JudgeAssignment).where(
                JudgeAssignment.judge_id == user.id,
                JudgeAssignment.project_id == project_id,
                JudgeAssignment.event_id == eid
            )
        ).scalar_one_or_none()
        return assignment is not None
    
    def require_judge_assignment(self, project_id: int, event_id: int) -> JudgeAssignment:
        user = self.require_judge(event_id)
        assignment = self.db.execute(
            select(JudgeAssignment).where(
                JudgeAssignment.judge_id == user.id,
                JudgeAssignment.project_id == project_id,
                JudgeAssignment.event_id == event_id
            )
        ).scalar_one_or_none()
        if not assignment:
            raise AuthorizationError("Not assigned to this project", status.HTTP_403_FORBIDDEN)
        return assignment
    
    def get_event(self, event_id: int) -> Optional[Event]:
        return self.db.get(Event, event_id)


def get_current_user_from_session(db: Session, session_token: str) -> Optional[User]:
    from app.core.security import verify_session_token
    from app.core.auth import AuthService
    
    payload = verify_session_token(session_token)
    if not payload:
        return None
    
    user_id = int(payload.get("sub", 0))
    auth_service = AuthService(db)
    return auth_service.get_user(user_id)
