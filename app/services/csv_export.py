"""CSV export service."""
import csv
import io
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    Event, Project, Team, TeamMember, User, Track,
    JudgeAssignment, Review, Score, Criterion, Rubric,
    Result, NormalizationRun, Vote, Comment
)


class CSVExportService:
    """Service for exporting data as CSV."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_event_summary(self, event_id: int) -> str:
        """Export a comprehensive event summary as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([
            "Project ID", "Project Title", "Team Name", "Track",
            "Status", "Submitted At",
            "Raw Aggregate", "Normalized Score", "Rank",
            "Review Count", "Criteria Count",
            "Total Votes", "Upvotes", "Downvotes",
            "Repo URL", "Demo URL", "Video URL"
        ])
        
        projects = self.db.execute(
            select(Project).where(Project.event_id == event_id)
        ).scalars().all()
        
        run = self.db.execute(
            select(NormalizationRun)
            .where(
                NormalizationRun.event_id == event_id,
                NormalizationRun.is_published == True
            )
            .order_by(NormalizationRun.completed_at.desc())
        ).scalar_one_or_none()
        
        results_map = {}
        if run:
            results = self.db.execute(
                select(Result).where(Result.run_id == run.id)
            ).scalars().all()
            results_map = {r.project_id: r for r in results}
        
        vote_counts = self._get_vote_counts(event_id)
        
        for project in projects:
            team = self.db.get(Team, project.team_id)
            track = self.db.get(Track, project.track_id) if project.track_id else None
            result = results_map.get(project.id)
            votes = vote_counts.get(project.id, {"total": 0, "up": 0, "down": 0})
            
            writer.writerow([
                project.id,
                self._sanitize_csv(project.title),
                self._sanitize_csv(team.name) if team else "",
                self._sanitize_csv(track.name) if track else "",
                project.status.value,
                project.submitted_at.isoformat() if project.submitted_at else "",
                float(result.raw_aggregate) if result and result.raw_aggregate else "",
                float(result.normalized_score) if result and result.normalized_score else "",
                result.rank if result else "",
                result.review_count if result else 0,
                result.criterion_count if result else 0,
                votes["total"],
                votes["up"],
                votes["down"],
                self._sanitize_csv(project.repo_url or ""),
                self._sanitize_csv(project.demo_url or ""),
                self._sanitize_csv(project.video_url or "")
            ])
        
        return output.getvalue()
    
    def export_judging_details(self, event_id: int) -> str:
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([
            "Project ID", "Project Title", "Judge ID", "Judge Name",
            "Assignment Status", "Review Status",
            "Criterion", "Weight", "Score", "Score Comment"
        ])
        
        assignments = self.db.execute(
            select(JudgeAssignment).where(JudgeAssignment.event_id == event_id)
        ).scalars().all()
        
        for assignment in assignments:
            project = self.db.get(Project, assignment.project_id)
            judge = self.db.get(User, assignment.judge_id)
            
            review = self.db.execute(
                select(Review).where(Review.assignment_id == assignment.id)
            ).scalar_one_or_none()
            
            if review:
                scores = self.db.execute(
                    select(Score).where(Score.review_id == review.id)
                ).scalars().all()
                
                for score in scores:
                    criterion = self.db.get(Criterion, score.criterion_id)
                    writer.writerow([
                        project.id if project else "",
                        self._sanitize_csv(project.title) if project else "",
                        judge.id if judge else "",
                        self._sanitize_csv(judge.display_name) if judge else "",
                        assignment.status.value,
                        review.status.value,
                        self._sanitize_csv(criterion.label) if criterion else "",
                        float(criterion.weight) if criterion else "",
                        float(score.value),
                        self._sanitize_csv(score.comment or "")
                    ])
            else:
                writer.writerow([
                    project.id if project else "",
                    self._sanitize_csv(project.title) if project else "",
                    judge.id if judge else "",
                    self._sanitize_csv(judge.display_name) if judge else "",
                    assignment.status.value,
                    "unstarted",
                    "", "", "", ""
                ])
        
        return output.getvalue()
    
    def export_teams(self, event_id: int) -> str:
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        writer.writerow([
            "Team ID", "Team Name", "Member Count",
            "Member 1", "Member 2", "Member 3", "Member 4"
        ])
        
        teams = self.db.execute(
            select(Team).where(Team.event_id == event_id)
        ).scalars().all()
        
        for team in teams:
            members = self.db.execute(
                select(TeamMember, User)
                .join(User, TeamMember.user_id == User.id)
                .where(TeamMember.team_id == team.id)
            ).all()
            
            member_names = [self._sanitize_csv(m[1].display_name) for m in members]
            while len(member_names) < 4:
                member_names.append("")
            
            writer.writerow([
                team.id,
                self._sanitize_csv(team.name),
                len(members),
                *member_names
            ])
        
        return output.getvalue()
    
    def _get_vote_counts(self, event_id: int) -> Dict[int, Dict[str, int]]:
        votes = self.db.execute(
            select(Vote).where(Vote.event_id == event_id)
        ).scalars().all()
        
        counts: Dict[int, Dict[str, int]] = {}
        for vote in votes:
            if vote.project_id not in counts:
                counts[vote.project_id] = {"total": 0, "up": 0, "down": 0}
            counts[vote.project_id]["total"] += 1
            if vote.value > 0:
                counts[vote.project_id]["up"] += 1
            else:
                counts[vote.project_id]["down"] += 1
        
        return counts
    
    def _sanitize_csv(self, value: str) -> str:
        if not value:
            return ""
        if value.startswith(('=', '+', '-', '@')):
            value = "'" + value
        return value
