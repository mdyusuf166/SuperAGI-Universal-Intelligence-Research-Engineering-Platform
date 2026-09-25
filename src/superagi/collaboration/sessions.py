"""Bounded in-process collaboration session."""

from __future__ import annotations

from .models import MAX_SESSION_ITEMS, CollaborationGoal, CollaborationSession, CollaborationTask, ConflictItem, ContextItem, Decision, InteractionMode, ProvenanceRef, Recommendation, Role


class SessionStore:
    def __init__(self, objective: str, mode: InteractionMode = InteractionMode.AI_ASSISTED) -> None:
        self.session = CollaborationSession(objective=objective, mode=mode)

    def _room(self, field: str, item) -> None:
        values = getattr(self.session, field)
        if len(values) >= MAX_SESSION_ITEMS:
            raise ValueError("Bounded session context is full")
        values.append(item)

    def add_participant(self, name: str) -> None:
        self._room("participants", name)

    def add_role(self, role: Role) -> None:
        self._room("roles", role)

    def add_context(self, item: ContextItem) -> None:
        self._room("context", item)

    def add_goal(self, goal: CollaborationGoal) -> None:
        self._room("goals", goal)

    def add_task(self, task: CollaborationTask) -> None:
        self._room("tasks", task)

    def add_constraint(self, text: str) -> None:
        self._room("constraints", text)

    def add_decision(self, decision: Decision) -> None:
        self._room("decisions", decision)

    def add_recommendation(self, recommendation: Recommendation) -> None:
        self._room("recommendations", recommendation)

    def add_question(self, question: str) -> None:
        self._room("unresolved_questions", question)

    def add_provenance(self, ref: ProvenanceRef) -> None:
        self._room("provenance", ref)

    def add_conflict(self, conflict: ConflictItem) -> None:
        self._room("conflicts", conflict)
