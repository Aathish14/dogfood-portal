from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Optional, List
from datetime import datetime, timezone

from app.core.config import settings
from app.core.database import get_db
from app.core.auth import AuthService
from app.core.authorization import Authz
from app.core.security import create_session_token, verify_session_token
from app.models import User, Role, Event, EventStatus, Project, ProjectStatus, Team, TeamMember, Track, Rubric, Criterion, JudgeAssignment, Review, Score, ReviewBatch
from app.schemas import (
    LoginRequest, LoginResponse, UserResponse,
    EventCreate, EventUpdate, EventResponse, EventWithDetails,
    TrackResponse, RubricResponse, CriterionResponse,
    TeamCreate, TeamUpdate, TeamResponse, JoinTeamRequest,
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
    return {"status": "healthy", "version": settings.app_version}


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    try:
        from sqlalchemy import text
        db.execute(select(1))
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not ready")

@router.get("/api/judge/assignments", response_model=List[AssignmentResponse])
async def get_judge_assignments(
    event_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    authz = Authz(db, current_user)
    authz.require_judge(event_id)
    assignments = db.execute(
        select(JudgeAssignment).where(
            JudgeAssignment.event_id == event_id,
            JudgeAssignment.judge_id == current_user.id
        )
    ).scalars().all()
    result = []
    for assignment in assignments:
        project = db.get(Project, assignment.project_id)
        review = db.execute(
            select(Review).where(Review.assignment_id == assignment.id)
        ).scalar_one_or_none()
        review_resp = None
    if review:
        scores = db.execute(
            select(Score).where(Score.review_id == review.id)
        ).scalars().all()
        score_responses = []
        for score in scores:
            criterion = db.get(Criterion, score.criterion_id)
            score_responses.append(ScoreResponse(
                id=score.id,
                criterion_id=score.criterion_id,
                criterion_label=criterion.label if criterion else "",
                weight=float(criterion.weight) if criterion else 0,
                value=float(score.value),
                comment=score.comment
            ))
        review_resp = ReviewResponse(
            id=review.id,
            assignment_id=review.assignment_id,
            judge_id=review.judge_id,
            status=review.status,
            general_comments=review.general_comments,
            submitted_at=review.submitted_at,
            scores=score_responses
        )
    result.append(AssignmentResponse(
        id=assignment.id,
        event_id=assignment.event_id,
        judge_id=assignment.judge_id,
        project_id=assignment.project_id,
        batch_id=assignment.batch_id,
        status=assignment.status,
        assigned_at=assignment.assigned_at,
        started_at=assignment.started_at,
        completed_at=assignment.completed_at,
        project_title=project.title if project else None,
        review=review_resp
    ))
    return result

@router.post("/api/judge/reviews/{assignment_id}", response_model=ReviewResponse)
async def submit_review(
    assignment_id: int,
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    assignment = db.get(JudgeAssignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    authz = Authz(db, current_user)
    authz.require_judge_assignment(assignment.project_id, assignment.event_id)
    review = db.execute(
        select(Review).where(Review.assignment_id == assignment_id)
    ).scalar_one_or_none()
    if not review:
        review = Review(assignment_id=assignment_id, judge_id=current_user.id)
        db.add(review)
        db.flush()
    review.general_comments = review_data.general_comments
    review.status = ReviewStatus.SUBMITTED
    review.submitted_at = datetime.now(timezone.utc)
    db.execute(
        Score.__table__.delete().where(Score.review_id == review.id)
    )
    for score_input in review_data.scores:
        criterion = db.get(Criterion, score_input.criterion_id)
        if not criterion:
            continue
        score = Score(
            review_id=review.id,
            criterion_id=score_input.criterion_id,
            value=score_input.value,
            comment=score_input.comment
        )
        db.add(score)
    assignment.status = AssignmentStatus.COMPLETED
    assignment.completed_at = datetime.now(timezone.utc)
    db.commit()
    scores = db.execute(
        select(Score).where(Score.review_id == review.id)
    ).scalars().all()
    score_responses = []
    for score in scores:
        criterion = db.get(Criterion, score.criterion_id)
        score_responses.append(ScoreResponse(
            id=score.id,
            criterion_id=score.criterion_id,
            criterion_label=criterion.label if criterion else "",
            weight=float(criterion.weight) if criterion else 0,
            value=float(score.value),
            comment=score.comment
        ))
    return ReviewResponse(
        id=review.id,
        assignment_id=review.assignment_id,
        judge_id=review.judge_id,
        status=review.status,
        general_comments=review.general_comments,
        submitted_at=review.submitted_at,
        scores=score_responses
    )

@router.get("/api/organizer/events/{event_id}/progress", response_model=JudgingProgressResponse)
async def get_judging_progress(
    event_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    authz = Authz(db, current_user)
    authz.require_organizer(event_id)
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    assignments = db.execute(
        select(JudgeAssignment).where(JudgeAssignment.event_id == event_id)
    ).scalars().all()
    total = len(assignments)
    completed = 0
    in_progress = 0
    unstarted = 0
    batch_stats = {}
    for assignment in assignments:
        review = db.execute(
            select(Review).where(Review.assignment_id == assignment.id)
        ).scalar_one_or_none()
    batch_id = assignment.batch_id or 0
    if batch_id not in batch_stats:
        batch_stats[batch_id] = {"total": 0, "completed": 0, "in_progress": 0, "unstarted": 0}
    batch_stats[batch_id]["total"] += 1
    if review and review.status == ReviewStatus.SUBMITTED:
        completed += 1
        batch_stats[batch_id]["completed"] += 1
    elif review and review.status in [ReviewStatus.DRAFT, ReviewStatus.IN_PROGRESS]:
        in_progress += 1
        batch_stats[batch_id]["in_progress"] += 1
    else:
        unstarted += 1
        batch_stats[batch_id]["unstarted"] += 1
    batches = db.execute(
        select(ReviewBatch).where(ReviewBatch.event_id == event_id)
    ).scalars().all()
    batch_names = {b.id: b.name for b in batches}
    batch_names[0] = "Unbatched"
    batch_progress = []
    for batch_id, stats in batch_stats.items():
        batch_progress.append(BatchProgressResponse(
            batch_id=batch_id,
            batch_name=batch_names.get(batch_id, f"Batch {batch_id}"),
            total_assignments=stats["total"],
            completed_assignments=stats["completed"],
            in_progress_assignments=stats["in_progress"],
            unstarted_assignments=stats["unstarted"],
            completion_rate=stats["completed"] / stats["total"] if stats["total"] > 0 else 0
        ))
    return JudgingProgressResponse(
    event_id=event_id,
    total_assignments=total,
    completed_reviews=completed,
    in_progress_reviews=in_progress,
    unstarted_reviews=unstarted,
    overall_completion_rate=completed / total if total > 0 else 0,
    batches=batch_progress
    )

@router.post("/api/organizer/events/{event_id}/normalize", response_model=NormalizationRunResponse)
async def run_normalization(
    event_id: int,
    run_data: NormalizationRunCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    authz = Authz(db, current_user)
    authz.require_organizer(event_id)
    service = NormalizationService(db)
    run = service.run_normalization(
        event_id=event_id,
        rubric_id=run_data.rubric_id,
        method=run_data.method,
        initiated_by=current_user.id,
        parameters=run_data.parameters
    )
    return NormalizationRunResponse.from_orm(run)

@router.get("/api/organizer/events/{event_id}/results", response_model=List[RunWithResultsResponse])
async def get_results(
    event_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    authz = Authz(db, current_user)
    authz.require_organizer(event_id)
    runs = db.execute(
        select(NormalizationRun).where(NormalizationRun.event_id == event_id)
        .order_by(NormalizationRun.created_at.desc())
    ).scalars().all()
    result = []
    for run in runs:
        run_resp = RunWithResultsResponse.from_orm(run)
        results = db.execute(
            select(Result).where(Result.run_id == run.id)
        ).scalars().all()
        run_resp.results = [ResultResponse.from_orm(r) for r in results]
        result.append(run_resp)
    return result

@router.post("/api/organizer/normalization/{run_id}/publish")
async def publish_results(
    run_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    run = db.get(NormalizationRun, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Normalization run not found")
    authz = Authz(db, current_user)
    authz.require_organizer(run.event_id)
    run.is_published = True
    run.published_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Results published"}

@router.get("/api/export.csv")
async def export_csv(
    event_id: int,
    type: str = "summary",
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    authz = Authz(db, current_user)
    authz.require_organizer(event_id)
    service = CSVExportService(db)
    if type == "summary":
        csv_content = service.export_event_summary(event_id)
        filename = f"event_{event_id}_summary.csv"
    elif type == "judging":
        csv_content = service.export_judging_details(event_id)
        filename = f"event_{event_id}_judging.csv"
    elif type == "teams":
        csv_content = service.export_teams(event_id)
        filename = f"event_{event_id}_teams.csv"
    else:
        raise HTTPException(status_code=400, detail="Invalid export type")
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/api/admin/seed")
async def seed_fixtures(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    authz = Authz(db, current_user)
    authz.require_organizer()
    counts = seed_database(db)
    credentials = get_checker_credentials(db)
    return {
        "message": "Database seeded successfully",
        "counts": counts,
        "checker_credentials": credentials
    }

@router.get("/api/admin/checker-credentials")
async def get_checker_creds(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    authz = Authz(db, current_user)
    authz.require_organizer()
    credentials = get_checker_credentials(db)
    return credentials

from sqlalchemy import select, func
from app.models import Team, TeamMember, Track, Rubric, Criterion, JudgeAssignment, Review, Score, ReviewBatch

print("Routes file complete")
