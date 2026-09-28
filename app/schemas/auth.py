"""Authentication schemas."""
from __future__ import annotations

from pydantic import BaseModel, EmailStr
from typing import Optional


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    email: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str
    email: Optional[EmailStr] = None
