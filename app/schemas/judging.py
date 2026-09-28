"""Judging schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

from app.models.judging import AssignmentStatus, ReviewStatus


class ScoreInput(BaseModel):
    criterion_id: int
    value: float = Field(ge=0, le=100)
    comment: Optional[str] = None


class ReviewCreate(BaseModel):
    scores: List[ScoreInput]
    general_comments: Optional[str] = None


class ReviewUpdate(BaseModel):
    scores: Optional[List[ScoreInput]] = None
    general_comments: Optional[str] = None
    status: Optional[ReviewStatus] = None


class ScoreResponse(BaseModel):
    id: int
    criterion_id: int
    criterion_label: str
    weight: float
    value: float
    comment: Optional[str]

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: int
    assignment_id: int
    judge_id: int
    status: ReviewStatus
    general_comments: Optional[str]
    submitted_at: Optional[datetime]
    scores: List[ScoreResponse] = []

    class Config:
        from_attributes = True


class AssignmentResponse(BaseModel):
    id: int
    event_id: int
    judge_id: int
    project_id: int
    batch_id: Optional[int]
    status: AssignmentStatus
    assigned_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    project_title: Optional[str] = None
    review: Optional[ReviewResponse] = None

    class Config:
        from_attributes = True


class BatchProgressResponse(BaseModel):
    batch_id: int
    batch_name: str
    total_assignments: int
    completed_assignments: int
    in_progress_assignments: int
    unstarted_assignments: int
    completion_rate: float


class JudgingProgressResponse(BaseModel):
    event_id: int
    total_assignments: int
    completed_reviews: int
    in_progress_reviews: int
    unstarted_reviews: int
    overall_completion_rate: float
    batches: List[BatchProgressResponse] = []
