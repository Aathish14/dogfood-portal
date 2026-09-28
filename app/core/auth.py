"""Authentication service - user management and login."""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.models.role import RoleMembership, Role
from app.core.security import verify_password, get_password_hash, create_session_token, verify_session_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        
        if user and verify_password(password, user.hashed_password):
            return user
        return None
    
    def create_user(self, username: str, password: str, display_name: str, email: Optional[str] = None) -> User:
        user = User(
            username=username,
            hashed_password=get_password_hash(password),
            display_name=display_name,
            email=email,
        )
        self.db.add(user)
        self.db.flush()
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
    
    def create_session(self, user: User, event_id: Optional[int] = None) -> str:
        role = "participant"
        if event_id:
            membership = self.db.execute(
                select(RoleMembership).where(
                    RoleMembership.user_id == user.id,
                    RoleMembership.event_id == event_id
                )
            ).scalar_one_or_none()
            if membership:
                role = membership.role.value
        return create_session_token(user.id, role, event_id)
    
    def verify_session(self, session_token: str) -> Optional[dict]:
        return verify_session_token(session_token)
    
    def assign_role(self, user_id: int, event_id: int, role: Role) -> RoleMembership:
        membership = RoleMembership(
            user_id=user_id,
            event_id=event_id,
            role=role,
        )
        self.db.add(membership)
        self.db.flush()
        return membership
    
    def get_user_roles(self, user_id: int, event_id: int) -> List[RoleMembership]:
        return self.db.execute(
            select(RoleMembership).where(
                RoleMembership.user_id == user_id,
                RoleMembership.event_id == event_id
            )
        ).scalars().all()
    
    def has_role(self, user_id: int, event_id: int, role: Role) -> bool:
        membership = self.db.execute(
            select(RoleMembership).where(
                RoleMembership.user_id == user_id,
                RoleMembership.event_id == event_id,
                RoleMembership.role == role
            )
        ).scalar_one_or_none()
        return membership is not None
