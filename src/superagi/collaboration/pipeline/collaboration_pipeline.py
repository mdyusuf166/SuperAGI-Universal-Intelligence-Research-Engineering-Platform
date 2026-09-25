"""Collaboration report pipeline. It drafts and reviews. It does not execute external actions."""

from __future__ import annotations

from superagi.core.models import Task
from superagi.core.planning import Planner
from superagi.personal.services import PersonalMemoryService

from ..context import ContextService
from ..coordination import CoordinationService
from ..decisions import DecisionSupport
from ..goals import GoalService
from ..models import ArtifactStatus, Claim, CollaborationConstraint, ContextItem, InteractionMode, ReviewSeverity
from ..provenance import ProvenanceLog
from ..recommendations import RecommendationEngine
from ..safety import ConsentGate, SafetyPolicy
from ..services import CollaborationReview
from ..sessions import SessionStore
from ..tasks import TaskCoordinator

STAGE_ORDER = [
    "objective",
    "context",
    "goals",
    "roles",
    "tasks",
    "dependencies",
    "agent_coordination",
    "evidence_results",
    "conflict_detection",
    "review",
    "recommendations",
    "human_approval",
    "final_report",
]


class CollaborationPipeline:
    def __init__(self, memory=None) -> None:
        self.memory = memory
        self.personal = PersonalMemoryService(memory) if memory is not None else None
        self.safety = SafetyPolicy()
        self.consent_gate = ConsentGate()

    def _stop(self, stage: str, reason: str, safety: dict) -> dict:
        index = STAGE_ORDER.index(stage)
        return {"status": "FAILED", "stage": stage, "reason": reason, "stages": STAGE_ORDER[: index + 1], "safety": safety, "executed": False, "classification": "ASSISTANCE_ONLY"}

    def run(self, objective: str, *, participants: list[str], roles: list, consent, mode: InteractionMode = InteractionMode.AI_ASSISTED, goal_statements: list[str], task_specs: list[dict], constraints: tuple[str, ...] = (), context_items: tuple[str, ...] = (), evidence: tuple[str, ...] = (), claims: list[Claim] | None = None, registry=None, capabilities: tuple[str, ...] = (), milestones: tuple[str, ...] = (), approval: bool = False, sources: tuple[str, ...] = ()) -> dict:
        safety = self.safety.assess(objective)
        if not safety["allowed"]:
            return self._stop("objective", "Safety policy rejected request.", safety)
        items = [ContextItem(text=text, source=sources[0] if sources else "session") for text in context_items]
        context = ContextService(self.memory, self.personal).build(items, consent)
        stored = {"persisted": False, "mode": "session-only"}
        if self.memory is not None:
            stored = ContextService(self.memory, self.personal).store(items, consent)
        goals = GoalService()
        created_goals = [goals.create(statement, priority=index + 1, milestones=milestones) for index, statement in enumerate(goal_statements)]
        store = SessionStore(objective, mode)
        for name in participants:
            store.add_participant(name)
        for role in roles:
            store.add_role(role)
        for item in context["items"]:
            store.add_context(item)
        for goal in created_goals:
            store.add_goal(goal)
        for constraint in constraints:
            store.add_constraint(constraint)
        coordinator = TaskCoordinator()
        created = []
        for spec in task_specs:
            created.append(coordinator.create(spec["title"], spec.get("owner", ""), priority=spec.get("priority", 0), evidence=tuple(spec.get("evidence", evidence)), blockers=tuple(spec.get("blockers", ())), completion_criteria=tuple(spec.get("completion_criteria", ("Human review",)))))
        by_title = {task.title: task for task in created}
        for spec, task in zip(task_specs, created):
            task.dependencies = [by_title[name].id for name in spec.get("depends_on", []) if name in by_title]
        ordered = coordinator.order(created)
        if ordered["cycle"]:
            failed = self._stop("dependencies", "Task dependencies contain a cycle.", safety)
            failed["blocked"] = ordered["blocked"]
            return failed
        for task in ordered["ordered"]:
            store.add_task(task)
        core_plan = Planner().create_plan(Task(description=objective))
        coordination = CoordinationService().coordinate(objective, registry, list(capabilities))
        for conflict in CoordinationService().claim_conflicts(list(claims or [])):
            store.add_conflict(conflict)
        provenance = ProvenanceLog()
        for source in sources:
            ref = provenance.record(source=source, originating_agent="collaboration_pipeline", session_id=store.session.id, evidence=list(evidence), memory=self.memory if stored.get("persisted") else None)
            if ref is not None:
                store.add_provenance(ref)
        review = CollaborationReview().review(store.session, approval_granted=approval, orchestration_conflicts=coordination["orchestration_conflicts"])
        support = DecisionSupport().prepare(question=objective, options=[{"name": "proceed with human review", "criteria": {"risk": 1, "effort": 1}, "evidence": list(evidence), "assumptions": ["The human confirms the next step."]}, {"name": "defer", "criteria": {"risk": 2, "effort": 2}, "evidence": list(evidence), "assumptions": ["No deadline was supplied."]}], criteria=["risk", "effort"], evidence=list(evidence), assumptions=["Recommendations are not decisions."], risks=["No external action is authorized."], tradeoffs="Lower explicit risk and effort sum is preferred.")
        action = RecommendationEngine().draft_action(support["recommendation"])
        if approval:
            support["decision"].approved = True
            support["decision"].status = "DECISION"
            action.status = ArtifactStatus.APPROVED_ACTION
        action.executed = False
        store.add_decision(support["decision"])
        store.add_recommendation(support["recommendation"])
        blocking = {item.category for item in review["findings"] if item.severity in {ReviewSeverity.ERROR, ReviewSeverity.CRITICAL}}
        if ReviewSeverity.CRITICAL in {item.severity for item in review["findings"]}:
            status = "FAILED"
        elif blocking == {"missing_approval"}:
            status = "AWAITING_HUMAN_APPROVAL"
        elif blocking:
            status = "FAILED"
        else:
            status = "COMPLETED"
        report = "Collaboration report only. Recommendations are not actions, proposals are not execution, and drafts are not approved actions."
        return {
            "status": status,
            "stages": list(STAGE_ORDER),
            "session": store.session,
            "context": context,
            "storage": stored,
            "goals": created_goals,
            "roles": roles,
            "tasks": ordered["ordered"],
            "core_plan": [step.description for step in core_plan.steps],
            "constraints": [CollaborationConstraint(kind="user", limit=item).limit for item in constraints],
            "coordination": coordination,
            "evidence": list(evidence),
            "conflicts": store.session.conflicts,
            "review": review,
            "recommendation": support["recommendation"],
            "decision": support["decision"],
            "action": action,
            "human_approval": {"required": mode in {InteractionMode.HUMAN_APPROVAL_REQUIRED, InteractionMode.HUMAN_REVIEW_REQUIRED}, "granted": approval, "executed": False},
            "report": report,
            "safety": safety,
            "provenance": store.session.provenance,
            "executed": False,
            "classification": "ASSISTANCE_ONLY",
        }
