"""Seed service - loads fixture data into the database."""
import json
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import (
    User, Role, RoleMembership, Event, EventStatus,
    Team, TeamMember, Track, Project, ProjectStatus,
    Rubric, Criterion, JudgeAssignment, ReviewBatch, Review, Score,
    AssignmentStatus, ReviewStatus
)
from app.core.security import get_password_hash


class SeedService:
    """Service for seeding the database with fixture data."""
    
    def __init__(self, db: Session, fixtures_path: str = "./fixtures/fixtures.json"):
        self.db = db
        self.fixtures_path = fixtures_path
        self.fixture_data: Optional[Dict] = None
        self.created_ids: Dict[str, Dict[str, int]] = {
            "users": {},
            "events": {},
            "tracks": {},
            "teams": {},
            "projects": {},
            "rubrics": {},
            "criteria": {},
            "judge_assignments": {},
            "review_batches": {},
            "reviews": {},
        }
    
    def load_fixtures(self) -> Dict:
        """Load fixture data from JSON file."""
        with open(self.fixtures_path, 'r') as f:
            self.fixture_data = json.load(f)
        return self.fixture_data
    
    def seed_all(self) -> Dict[str, int]:
        """Seed all fixture data. Returns counts of created entities."""
        if not self.fixture_data:
            self.load_fixtures()
        
        counts = {}
        
        # Seed in dependency order
        counts["users"] = self._seed_users()
        counts["event"] = self._seed_event()
        counts["tracks"] = self._seed_tracks()
        counts["rubric"] = self._seed_rubric()
        counts["teams"] = self._seed_teams()
        counts["projects"] = self._seed_projects()
        counts["judge_assignments"] = self._seed_judge_assignments()
        counts["scores"] = self._seed_scores()
        
        self.db.commit()
        return counts
    
    def _seed_users(self) -> int:
        """Seed users (organizers, judges, participants)."""
        count = 0
        
        # Organizer
        organizer_data = self.fixture_data.get("organizer", {})
        if organizer_data:
            user = self._get_or_create_user(
                username=organizer_data.get("id", "organizer"),
                password="org_pass_2026",
                display_name=organizer_data.get("name", "Event Organizer"),
                email=organizer_data.get("email"),
                is_fixture=True
            )
            self.created_ids["users"][organizer_data.get("id", "organizer")] = user.id
            count += 1
        
        # Judges
        for judge_data in self.fixture_data.get("judges", []):
            user = self._get_or_create_user(
                username=judge_data["id"],
                password="judge_pass_2026",
                display_name=judge_data["name"],
                email=judge_data.get("email"),
                is_fixture=True
            )
            self.created_ids["users"][judge_data["id"]] = user.id
            count += 1
        
        # Participants (from team members)
        for team_data in self.fixture_data.get("teams", []):
            for member_email in team_data.get("members", []):
                username = member_email.replace("@", "_").replace(".", "_")
                user = self._get_or_create_user(
                    username=username,
                    password="part_pass_2026",
                    display_name=member_email,
                    email=member_email,
                    is_fixture=True
                )
                self.created_ids["users"][member_email] = user.id
                count += 1
        
        return count
    
    def _get_or_create_user(self, username: str, password: str, display_name: str, 
                           email: Optional[str], is_fixture: bool) -> User:
        """Get existing user or create new one."""
        user = self.db.execute(
            select(User).where(User.username == username)
        ).scalar_one_or_none()
        
        if not user:
            user = User(
                username=username,
                hashed_password=get_password_hash(password),
                display_name=display_name,
                email=email,
                is_fixture=is_fixture
            )
            self.db.add(user)
            self.db.flush()
        
        return user
    
    def _seed_event(self) -> int:
        """Seed the main event."""
        event_data = self.fixture_data["event"]
        
        event = self.db.execute(
            select(Event).where(Event.title == event_data["name"])
        ).scalar_one_or_none()
        
        if not event:
            event = Event(
                title=event_data["name"],
                description="DOGFOOD 2026 Hackathon",
                status=EventStatus.JUDGING,
                submissions_close=self._parse_dt(event_data.get("submissions_close")),
                is_fixture=True
            )
            self.db.add(event)
            self.db.flush()
        
        self.created_ids["events"]["main"] = event.id
        
        # Assign organizer role
        organizer_id = self.created_ids["users"].get("organizer")
        if organizer_id:
            self._assign_role(organizer_id, event.id, Role.ORGANIZER)
        
        # Assign judge roles
        for judge_data in self.fixture_data.get("judges", []):
            judge_id = self.created_ids["users"].get(judge_data["id"])
            if judge_id:
                self._assign_role(judge_id, event.id, Role.JUDGE)
        
        # Assign participant roles
        for team_data in self.fixture_data.get("teams", []):
            for member_email in team_data.get("members", []):
                part_id = self.created_ids["users"].get(member_email)
                if part_id:
                    self._assign_role(part_id, event.id, Role.PARTICIPANT)
        
        return 1
    
    def _assign_role(self, user_id: int, event_id: int, role: Role) -> RoleMembership:
        """Assign a role to a user for an event."""
        membership = self.db.execute(
            select(RoleMembership).where(
                RoleMembership.user_id == user_id,
                RoleMembership.event_id == event_id,
                RoleMembership.role == role
            )
        ).scalar_one_or_none()
        
        if not membership:
            membership = RoleMembership(
                user_id=user_id,
                event_id=event_id,
                role=role
            )
            self.db.add(membership)
            self.db.flush()
        
        return membership
    
    def _seed_tracks(self) -> int:
        """Seed tracks."""
        event_id = self.created_ids["events"]["main"]
        count = 0
        
        for track_data in self.fixture_data.get("tracks", []):
            track = self.db.execute(
                select(Track).where(
                    Track.event_id == event_id,
                    Track.name == track_data["name"]
                )
            ).scalar_one_or_none()
            
            if not track:
                track = Track(
                    event_id=event_id,
                    name=track_data["name"],
                    is_fixture=True
                )
                self.db.add(track)
                self.db.flush()
            
            self.created_ids["tracks"][track_data["id"]] = track.id
            count += 1
        
        return count
    
    def _seed_rubric(self) -> int:
        """Seed rubric and criteria."""
        event_id = self.created_ids["events"]["main"]
        
        rubric = self.db.execute(
            select(Rubric).where(
                Rubric.event_id == event_id,
                Rubric.name == "Standard Judging Rubric"
            )
        ).scalar_one_or_none()
        
        if not rubric:
            rubric = Rubric(
                event_id=event_id,
                name="Standard Judging Rubric",
                description="Default rubric for DOGFOOD 2026",
                is_fixture=True
            )
            self.db.add(rubric)
            self.db.flush()
        
        self.created_ids["rubrics"]["main"] = rubric.id
        
        # Seed criteria from fixture scores structure
        criteria_data = [
            {"label": "functionality", "weight": 1.0, "scale_min": 1, "scale_max": 5, "display_order": 1},
            {"label": "quality", "weight": 1.0, "scale_min": 1, "scale_max": 5, "display_order": 2},
            {"label": "innovation", "weight": 1.0, "scale_min": 1, "scale_max": 5, "display_order": 3},
        ]
        
        for i, crit_data in enumerate(criteria_data):
            criterion = self.db.execute(
                select(Criterion).where(
                    Criterion.rubric_id == rubric.id,
                    Criterion.label == crit_data["label"]
                )
            ).scalar_one_or_none()
            
            if not criterion:
                criterion = Criterion(
                    rubric_id=rubric.id,
                    label=crit_data["label"],
                    weight=crit_data["weight"],
                    scale_min=crit_data["scale_min"],
                    scale_max=crit_data["scale_max"],
                    display_order=crit_data["display_order"],
                    is_fixture=True
                )
                self.db.add(criterion)
                self.db.flush()
            
            self.created_ids["criteria"][crit_data["label"]] = criterion.id
        
        return 1
    
    def _seed_teams(self) -> int:
        """Seed teams and team memberships."""
        event_id = self.created_ids["events"]["main"]
        count = 0
        
        for team_data in self.fixture_data.get("teams", []):
            team = self.db.execute(
                select(Team).where(
                    Team.event_id == event_id,
                    Team.name == team_data["name"]
                )
            ).scalar_one_or_none()
            
            if not team:
                team = Team(
                    event_id=event_id,
                    name=team_data["name"],
                    is_fixture=True
                )
                self.db.add(team)
                self.db.flush()
            
            self.created_ids["teams"][team_data["id"]] = team.id
            count += 1
            
            # Add team members
            for member_email in team_data.get("members", []):
                user_id = self.created_ids["users"].get(member_email)
                if user_id:
                    member = self.db.execute(
                        select(TeamMember).where(
                            TeamMember.team_id == team.id,
                            TeamMember.user_id == user_id
                        )
                    ).scalar_one_or_none()
                    
                    if not member:
                        member = TeamMember(
                            team_id=team.id,
                            user_id=user_id,
                            is_leader=False
                        )
                        self.db.add(member)
                        self.db.flush()
        
        # Set first member of each team as leader
        for team_data in self.fixture_data.get("teams", []):
            team_id = self.created_ids["teams"][team_data["id"]]
            first_member_email = team_data["members"][0]
            user_id = self.created_ids["users"][first_member_email]
            
            member = self.db.execute(
                select(TeamMember).where(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == user_id
                )
            ).scalar_one_or_none()
            
            if member:
                member.is_leader = True
        
        return count
    
    def _seed_projects(self) -> int:
        """Seed projects."""
        event_id = self.created_ids["events"]["main"]
        count = 0
        
        for project_data in self.fixture_data.get("projects", []):
            team_id = self.created_ids["teams"].get(project_data["team"])
            track_id = self.created_ids["tracks"].get(project_data.get("track"))
            
            if not team_id:
                continue
            
            project = self.db.execute(
                select(Project).where(
                    Project.event_id == event_id,
                    Project.title == project_data["title"]
                )
            ).scalar_one_or_none()
            
            if not project:
                project = Project(
                    event_id=event_id,
                    team_id=team_id,
                    track_id=track_id,
                    title=project_data["title"],
                    description=project_data.get("summary", ""),
                    repo_url=project_data.get("repo_url"),
                    demo_url=project_data.get("demo_url"),
                    video_url=project_data.get("video_url"),
                    status=ProjectStatus(project_data.get("status", "submitted")),
                    submitted_at=self._parse_dt(project_data.get("submitted_at")),
                    is_fixture=True
                )
                self.db.add(project)
                self.db.flush()
            
            self.created_ids["projects"][project_data["id"]] = project.id
            count += 1
        
        # Handle duplicate_of relationship
        for project_data in self.fixture_data.get("projects", []):
            if project_data.get("is_duplicate") and project_data.get("duplicate_of"):
                project_id = self.created_ids["projects"].get(project_data["title"])
                original_id = self.created_ids["projects"].get(project_data["duplicate_of"])
                if project_id and original_id:
                    project = self.db.get(Project, project_id)
                    if project:
                        project.duplicate_of_id = original_id
        
        return count
    
    def _seed_judge_assignments(self) -> int:
        """Seed judge assignments and review batches."""
        event_id = self.created_ids["events"]["main"]
        
        # Create review batches
        batch1 = self.db.execute(
            select(ReviewBatch).where(
                ReviewBatch.event_id == event_id,
                ReviewBatch.name == "Batch 1"
            )
        ).scalar_one_or_none()
        
        if not batch1:
            batch1 = ReviewBatch(
                event_id=event_id,
                name="Batch 1",
                description="First review batch",
                is_fixture=True
            )
            self.db.add(batch1)
            self.db.flush()
        
        batch2 = self.db.execute(
            select(ReviewBatch).where(
                ReviewBatch.event_id == event_id,
                ReviewBatch.name == "Batch 2"
            )
        ).scalar_one_or_none()
        
        if not batch2:
            batch2 = ReviewBatch(
                event_id=event_id,
                name="Batch 2",
                description="Second review batch (incomplete)",
                is_fixture=True
            )
            self.db.add(batch2)
            self.db.flush()
        
        self.created_ids["review_batches"]["batch_01"] = batch1.id
        self.created_ids["review_batches"]["batch_02"] = batch2.id
        
        # Create judge assignments from fixture scores
        count = 0
        batch_assignments = 0
        
        # Get all unique judge-project pairs from scores
        judge_projects = {}
        for score_data in self.fixture_data.get("scores", []):
            judge_username = score_data["judge"]
            project_id_str = score_data["project"]
            
            judge_id = self.created_ids["users"].get(judge_username)
            project_db_id = self.created_ids["projects"].get(project_id_str)
            
            if judge_id and project_db_id:
                key = (judge_id, project_db_id)
                if key not in judge_projects:
                    judge_projects[key] = {"judge_id": judge_id, "project_id": project_db_id}
        
        for key, data in judge_projects.items():
            judge_id = data["judge_id"]
            project_id = data["project_id"]
            
            # Alternate between batches
            batch_id = batch1.id if batch_assignments % 2 == 0 else batch2.id
            batch_assignments += 1
            
            assignment = self.db.execute(
                select(JudgeAssignment).where(
                    JudgeAssignment.event_id == event_id,
                    JudgeAssignment.judge_id == judge_id,
                    JudgeAssignment.project_id == project_id
                )
            ).scalar_one_or_none()
            
            if not assignment:
                assignment = JudgeAssignment(
                    event_id=event_id,
                    judge_id=judge_id,
                    project_id=project_id,
                    batch_id=batch_id,
                    status=AssignmentStatus.ASSIGNED,
                    is_fixture=True
                )
                self.db.add(assignment)
                self.db.flush()
            
            # Create review for this assignment
            review = self.db.execute(
                select(Review).where(Review.assignment_id == assignment.id)
            ).scalar_one_or_none()
            
            if not review:
                review = Review(
                    assignment_id=assignment.id,
                    judge_id=judge_id,
                    status=ReviewStatus.SUBMITTED,
                    is_fixture=True
                )
                self.db.add(review)
                self.db.flush()
            
            self.created_ids["judge_assignments"][f"{judge_id}_{project_id}"] = assignment.id
            count += 1
        
        return count
    
    def _seed_scores(self) -> int:
        """Seed scores for reviews."""
        # Get rubric criteria
        rubric_id = self.created_ids["rubrics"]["main"]
        criteria = self.db.execute(
            select(Criterion).where(Criterion.rubric_id == rubric_id)
        ).scalars().all()
        
        criterion_map = {c.label: c.id for c in criteria}
        
        count = 0
        
        # For each judge assignment, create scores from fixture data
        for score_data in self.fixture_data.get("scores", []):
            judge_username = score_data["judge"]
            project_id_str = score_data["project"]
            
            judge_id = self.created_ids["users"].get(judge_username)
            project_db_id = self.created_ids["projects"].get(project_id_str)
            
            if not judge_id or not project_db_id:
                continue
            
            # Find assignment
            assignment = self.db.execute(
                select(JudgeAssignment).where(
                    JudgeAssignment.event_id == self.created_ids["events"]["main"],
                    JudgeAssignment.judge_id == judge_id,
                    JudgeAssignment.project_id == project_db_id
                )
            ).scalar_one_or_none()
            
            if not assignment:
                continue
            
            # Get review for this assignment
            review = self.db.execute(
                select(Review).where(Review.assignment_id == assignment.id)
            ).scalar_one_or_none()
            
            if not review:
                continue
            
            criteria_scores = score_data.get("criteria", {})
            
            for criterion_label, score_value in criteria_scores.items():
                criterion_id = criterion_map.get(criterion_label)
                if not criterion_id:
                    continue
                
                score = self.db.execute(
                    select(Score).where(
                        Score.review_id == review.id,
                        Score.criterion_id == criterion_id
                    )
                ).scalar_one_or_none()
                
                if not score:
                    score = Score(
                        review_id=review.id,
                        criterion_id=criterion_id,
                        value=float(score_value),
                        is_fixture=True
                    )
                    self.db.add(score)
                    self.db.flush()
                    count += 1
        
        return count
    
    def _parse_dt(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not dt_str:
            return None
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    
    def _generate_realistic_score(self, criterion: Criterion) -> float:
        """Generate a realistic score for a criterion."""
        base = 70
        variation = 20
        score = base + random.uniform(-variation, variation)
        return max(criterion.scale_min, min(criterion.scale_max, round(score, 2)))
    
    def _parse_dt(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO datetime string."""
        if not dt_str:
            return None
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    
    def get_checker_credentials(self) -> Dict[str, str]:
        """Get the four checker credentials as session cookies."""
        event_id = self.created_ids["events"]["main"]
        
        credentials = {}
        
        # Organizer
        org_id = self.created_ids["users"].get("organizer")
        if org_id:
            from app.core.security import create_session_token
            token = create_session_token(org_id, "organizer", event_id)
            credentials["organizer"] = f"Cookie: session={token}"
        
        # Judge A (first judge)
        judge_a_id = self.created_ids["users"].get("jdg_01")
        if judge_a_id:
            from app.core.security import create_session_token
            token = create_session_token(judge_a_id, "judge", event_id)
            credentials["judge_a"] = f"Cookie: session={token}"
        
        # Judge B (second judge)
        judge_b_id = self.created_ids["users"].get("jdg_02")
        if judge_b_id:
            from app.core.security import create_session_token
            token = create_session_token(judge_b_id, "judge", event_id)
            credentials["judge_b"] = f"Cookie: session={token}"
        
        # Participant
        part_id = self.created_ids["users"].get("participant_01")
        if part_id:
            from app.core.security import create_session_token
            token = create_session_token(part_id, "participant", event_id)
            credentials["participant"] = f"Cookie: session={token}"
        
        return credentials


def seed_database(db: Session, fixtures_path: str = "./fixtures/fixtures.json") -> Dict[str, int]:
    """Convenience function to seed the database."""
    service = SeedService(db, fixtures_path)
    return service.seed_all()


def get_checker_credentials(db: Session, fixtures_path: str = "./fixtures/fixtures.json") -> Dict[str, str]:
    """Get checker credentials after seeding."""
    service = SeedService(db, fixtures_path)
    if not service.fixture_data:
        service.load_fixtures()
    return service.get_checker_credentials()
