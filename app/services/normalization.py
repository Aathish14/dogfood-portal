"""Normalization service - cross-judge score normalization."""
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    NormalizationRun, Result, Project, Review, Score, Criterion,
    JudgeAssignment, NormalizationMethod, Rubric, ReviewStatus
)


@dataclass
class JudgeStats:
    judge_id: int
    mean: float
    std: float
    count: int


@dataclass
class ProjectScores:
    project_id: int
    judge_scores: Dict[int, float]
    raw_average: float


class NormalizationService:
    """Service for cross-judge normalization."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def run_normalization(
        self,
        event_id: int,
        rubric_id: int,
        method: NormalizationMethod,
        initiated_by: int,
        parameters: Optional[Dict] = None
    ) -> NormalizationRun:
        """Run normalization and create results."""
        project_scores = self._collect_project_scores(event_id, rubric_id)
        
        if not project_scores:
            raise ValueError("No completed reviews found for normalization")
        
        if method == NormalizationMethod.Z_SCORE:
            normalized_scores = self._z_score_normalize(project_scores)
        elif method == NormalizationMethod.ROBUST_Z_SCORE:
            normalized_scores = self._robust_z_score_normalize(project_scores)
        elif method == NormalizationMethod.PERCENTILE:
            normalized_scores = self._percentile_normalize(project_scores)
        elif method == NormalizationMethod.RAW_AVERAGE:
            normalized_scores = self._raw_average_normalize(project_scores)
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        run = NormalizationRun(
            event_id=event_id,
            rubric_id=rubric_id,
            method=method,
            parameters=str(parameters) if parameters else None,
            initiated_by=initiated_by,
            completed_at=datetime.now(timezone.utc),
            is_published=False
        )
        self.db.add(run)
        self.db.flush()
        
        self._create_results(run.id, project_scores, normalized_scores)
        
        self.db.commit()
        return run
    
    def _collect_project_scores(self, event_id: int, rubric_id: int) -> List:
        """Collect raw scores for each project from each judge."""
        criteria = self.db.execute(
            select(Criterion).where(Criterion.rubric_id == rubric_id)
        ).scalars().all()
        criterion_ids = [c.id for c in criteria]
        
        if not criterion_ids:
            return []
        
        reviews = self.db.execute(
            select(Review)
            .join(JudgeAssignment, Review.assignment_id == JudgeAssignment.id)
            .where(
                JudgeAssignment.event_id == event_id,
                Review.status == ReviewStatus.SUBMITTED
            )
        ).scalars().all()
        
        project_judge_scores: Dict[int, Dict[int, List[float]]] = {}
        
        for review in reviews:
            assignment = self.db.get(JudgeAssignment, review.assignment_id)
            if not assignment:
                continue
            
            project_id = assignment.project_id
            judge_id = assignment.judge_id
            
            if project_id not in project_judge_scores:
                project_judge_scores[project_id] = {}
            if judge_id not in project_judge_scores[project_id]:
                project_judge_scores[project_id][judge_id] = []
            
            scores = self.db.execute(
                select(Score).where(Score.review_id == review.id)
            ).scalars().all()
            
            for score in scores:
                project_judge_scores[project_id][judge_id].append(float(score.value))
        
        project_scores = []
        for project_id, judge_scores in project_judge_scores.items():
            judge_aggregates = {}
            for judge_id, scores in judge_scores.items():
                if scores:
                    judge_aggregates[judge_id] = sum(scores) / len(scores)
            
            if judge_aggregates:
                raw_average = sum(judge_aggregates.values()) / len(judge_aggregates)
                project_scores.append(
                    type('ProjectScores', (), {
                        'project_id': project_id,
                        'judge_scores': judge_aggregates,
                        'raw_average': raw_average
                    })()
                )
        
        return project_scores
    
    def _z_score_normalize(self, project_scores) -> Dict[int, float]:
        judge_scores: Dict[int, List[float]] = {}
        for ps in project_scores:
            for judge_id, score in ps.judge_scores.items():
                if judge_id not in judge_scores:
                    judge_scores[judge_id] = []
                judge_scores[judge_id].append(score)
        
        judge_stats = {}
        for judge_id, scores in judge_scores.items():
            if len(scores) > 1:
                mean = statistics.mean(scores)
                std = statistics.stdev(scores)
            else:
                mean = scores[0]
                std = 0.0
            
            judge_stats[judge_id] = type('JudgeStats', (), {
                'judge_id': judge_id,
                'mean': mean,
                'std': std,
                'count': len(scores)
            })()
        
        normalized = {}
        for ps in project_scores:
            project_normalized_scores = []
            for judge_id, raw_score in ps.judge_scores.items():
                stats = judge_stats[judge_id]
                if stats.std > 0:
                    z_score = (raw_score - stats.mean) / stats.std
                else:
                    z_score = 0.0
                project_normalized_scores.append(z_score)
            
            if project_normalized_scores:
                normalized[ps.project_id] = statistics.mean(project_normalized_scores)
            else:
                normalized[ps.project_id] = 0.0
        
        return normalized
    
    def _robust_z_score_normalize(self, project_scores) -> Dict[int, float]:
        judge_scores: Dict[int, List[float]] = {}
        for ps in project_scores:
            for judge_id, score in ps.judge_scores.items():
                if judge_id not in judge_scores:
                    judge_scores[judge_id] = []
                judge_scores[judge_id].append(score)
        
        judge_stats = {}
        for judge_id, scores in judge_scores.items():
            median = statistics.median(scores)
            mad = statistics.median([abs(s - median) for s in scores])
            scaled_mad = mad * 1.4826 if mad > 0 else 0
            judge_stats[judge_id] = (median, scaled_mad)
        
        normalized = {}
        for ps in project_scores:
            project_normalized_scores = []
            for judge_id, raw_score in ps.judge_scores.items():
                median, mad = judge_stats[judge_id]
                if mad > 0:
                    z_score = (raw_score - median) / mad
                else:
                    z_score = 0.0
                project_normalized_scores.append(z_score)
            
            if project_normalized_scores:
                normalized[ps.project_id] = statistics.mean(project_normalized_scores)
            else:
                normalized[ps.project_id] = 0.0
        
        return normalized
    
    def _percentile_normalize(self, project_scores) -> Dict[int, float]:
        judge_scores: Dict[int, List[float]] = {}
        for ps in project_scores:
            for judge_id, score in ps.judge_scores.items():
                if judge_id not in judge_scores:
                    judge_scores[judge_id] = []
                judge_scores[judge_id].append(score)
        
        judge_percentiles: Dict[int, Dict[float, float]] = {}
        for judge_id, scores in judge_scores.items():
            sorted_scores = sorted(scores)
            n = len(sorted_scores)
            percentile_map = {}
            for i, score in enumerate(sorted_scores):
                percentile = (i + 0.5) / n
                percentile_map[score] = percentile
            judge_percentiles[judge_id] = percentile_map
        
        normalized = {}
        for ps in project_scores:
            project_percentiles = []
            for judge_id, raw_score in ps.judge_scores.items():
                percentile = judge_percentiles[judge_id].get(raw_score, 0.5)
                project_percentiles.append(percentile)
            
            if project_percentiles:
                normalized[ps.project_id] = statistics.mean(project_percentiles)
            else:
                normalized[ps.project_id] = 0.5
        
        return normalized
    
    def _raw_average_normalize(self, project_scores) -> Dict[int, float]:
        return {ps.project_id: ps.raw_average for ps in project_scores}
    
    def _create_results(
        self,
        run_id: int,
        project_scores,
        normalized_scores: Dict[int, float]
    ) -> List:
        results = []
        
        sorted_projects = sorted(
            project_scores,
            key=lambda ps: normalized_scores.get(ps.project_id, 0),
            reverse=True
        )
        
        for rank, ps in enumerate(sorted_projects, 1):
            result = Result(
                run_id=run_id,
                project_id=ps.project_id,
                raw_aggregate=ps.raw_average,
                normalized_score=normalized_scores.get(ps.project_id),
                rank=rank,
                review_count=len(ps.judge_scores),
                criterion_count=0
            )
            self.db.add(result)
            results.append(result)
        
        self.db.flush()
        return results


from datetime import datetime, timezone
import statistics
from typing import Dict, List, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    NormalizationRun, Result, Project, Review, Score, Criterion,
    JudgeAssignment, NormalizationMethod, Rubric, ReviewStatus
)

@dataclass
class JudgeStats:
    judge_id: int
    mean: float
    std: float
    count: int


@dataclass
class ProjectScores:
    project_id: int
    judge_scores: Dict[int, float]
    raw_average: float
