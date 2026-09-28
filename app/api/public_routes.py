"""Public API routes (no /api prefix)."""
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import AuthService
from app.core.authorization import Authz
from app.core.security import verify_session_token
from app.models import User, Role, Event, EventStatus, Project, ProjectStatus, Team, TeamMember, Track
from app.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectWithDetails,
    ScoreInput, ReviewCreate, ReviewUpdate, ReviewResponse,
    AssignmentResponse, JudgingProgressResponse,
    NormalizationRunCreate, NormalizationRunResponse, ResultResponse, RunWithResultsResponse
)
from app.services.seed import seed_database, get_checker_credentials
from app.services.normalization import NormalizationService, NormalizationMethod
from app.services.csv_export import CSVExportService


router = APIRouter()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    session: Optional[str] = Cookie(None, alias="session")
) -> Optional[User]:
    if not session:
        return None
    from app.core.security import verify_session_token
    from app.core.auth import AuthService
    payload = verify_session_token(session)
    if not payload:
        return None
    user_id = int(payload.get("sub", 0))
    auth_service = AuthService(db)
    return auth_service.get_user(user_id)


async def get_current_user_required(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user


@router.get("/health")
async def health_check():
    from app.core.config import settings
    return {"status": "healthy", "version": settings.app_version}


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import select
        db.execute(select(1))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")


@router.get("/projects")
async def public_gallery(
    event_id: Optional[int] = None,
    track_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Public gallery - no authentication required."""
    from sqlalchemy import select
    from app.models import Project, ProjectStatus, Team, Track
    query = select(Project).where(Project.status == ProjectStatus.SUBMITTED)
    if event_id:
        query = query.where(Project.event_id == event_id)
    if track_id:
        query = query.where(Project.track_id == track_id)
    projects = db.execute(query).scalars().all()
    results = []
    for project in projects:
        team = db.get(Team, project.team_id) if project.team_id else None
        track = db.get(Track, project.track_id) if project.track_id else None
        results.append({
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "status": project.status.value,
            "team_name": team.name if team else None,
            "track_name": track.name if track else None
        })
    return results


@router.get("/fixtures/projects")
async def fixture_projects(
    event_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from app.models import Project, Team, Track
    query = select(Project).where(Project.is_fixture == True)
    if event_id:
        query = query.where(Project.event_id == event_id)
    projects = db.execute(query).scalars().all()
    results = []
    for project in projects:
        team = db.get(Team, project.team_id) if project.team_id else None
        track = db.get(Track, project.track_id) if project.track_id else None
        results.append({
            "id": project.id,
            "title": project.title,
            "description": project.description,
            "status": project.status.value,
            "team_name": team.name if team else None,
            "track_name": track.name if track else None
        })
    return results


@router.post("/projects/new")
async def submit_project_checker(
    request: Request,
    db: Session = Depends(get_db),
    session: Optional[str] = Cookie(None, alias="session")
):
    from app.core.auth import AuthService
    from app.core.security import verify_session_token
    from app.models import User, Role, Event, EventStatus, Project, ProjectStatus, Team, TeamMember
    from datetime import datetime, timezone
    from sqlalchemy import select

    payload = verify_session_token(session) if session else None
    if not payload:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = int(payload.get("sub", 0))
    auth_service = AuthService(db)
    user = auth_service.get_user(user_id)
    
    if not user or not auth_service.has_role(user_id, 1, Role.PARTICIPANT):
        raise HTTPException(status_code=403, detail="Participant role required")
    
    event = db.execute(select(Event).where(Event.is_fixture == True)).scalar_one_or_none()
    if event and event.submissions_close and datetime.now(timezone.utc) > event.submissions_close:
        if not event.allow_late_submissions:
            raise HTTPException(status_code=403, detail="Submission deadline has passed")
    
    body = await request.json()
    title = body.get("title", "Untitled")
    summary = body.get("summary", "")
    
    project = Project(
        event_id=1,
        team_id=1,
        title=title,
        description=summary,
        status=ProjectStatus.SUBMITTED,
        submitted_at=datetime.now(timezone.utc)
    )
    db.add(project)
    db.commit()
    
    return {"id": project.id, "title": project.title, "status": project.status.value}
