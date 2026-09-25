"""User-controlled goals. Proposed steps do not replace the user's statement."""

from __future__ import annotations

from superagi.personal.services import GoalManager

from .models import CollaborationGoal, Milestone


class GoalService:
    def __init__(self) -> None:
        self.goals: dict = {}

    def create(self, statement: str, priority: int = 0, milestones: tuple[str, ...] = (), dependencies: tuple = ()) -> CollaborationGoal:
        goal = CollaborationGoal(statement=statement, priority=priority, milestones=[Milestone(name=name) for name in milestones], dependencies=list(dependencies))
        self.goals[goal.id] = goal
        return goal

    def decompose(self, goal: CollaborationGoal, parts: list[str]) -> list[CollaborationGoal]:
        proposed = []
        for part in parts:
            child = CollaborationGoal(statement=part, priority=goal.priority, proposed=True, parent_id=goal.id, status="PROPOSED")
            self.goals[child.id] = child
            proposed.append(child)
        return proposed

    def add_evidence(self, goal: CollaborationGoal, evidence: str) -> CollaborationGoal:
        goal.progress_evidence.append(evidence)
        return goal

    def complete(self, goal: CollaborationGoal, *, user_authorized: bool) -> CollaborationGoal:
        if not user_authorized:
            raise PermissionError("The system cannot close a user goal")
        goal.status = "COMPLETED"
        return goal

    def rename(self, goal: CollaborationGoal, statement: str, *, user_authorized: bool) -> CollaborationGoal:
        if not user_authorized:
            raise PermissionError("The system cannot redefine a user goal")
        goal.statement = statement
        return goal

    def prioritize(self) -> list[CollaborationGoal]:
        return sorted(self.goals.values(), key=lambda goal: (-goal.priority, goal.statement))

    def publish(self, goal: CollaborationGoal, manager: GoalManager, *, persistent_consent: bool) -> object:
        if not persistent_consent:
            raise PermissionError("Persistent consent is required before saving a personal goal")
        created = manager.create(goal.statement, goal.priority, tuple(item.name for item in goal.milestones))
        goal.personal_goal_id = created.id
        return created
