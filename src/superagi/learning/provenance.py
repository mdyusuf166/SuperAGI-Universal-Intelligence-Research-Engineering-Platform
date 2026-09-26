"""Provenance notes and the learning lifecycle state machine."""

from __future__ import annotations

from .models import LearningLifecycle, Provenance


def provenance(source: str | None, *, agent: str | None = None, evidence: list[str] | None = None) -> Provenance:
    cleaned = source.strip() if isinstance(source, str) else ""
    return Provenance(source=cleaned or None, status="PRESENT" if cleaned else "MISSING", agent=agent, evidence_refs=list(evidence or []))


_NEXT = {
    LearningLifecycle.IDENTIFIED: {LearningLifecycle.PROPOSED, LearningLifecycle.REJECTED, LearningLifecycle.FAILED},
    LearningLifecycle.PROPOSED: {LearningLifecycle.PLANNED, LearningLifecycle.REJECTED, LearningLifecycle.FAILED},
    LearningLifecycle.PLANNED: {LearningLifecycle.PRACTICING, LearningLifecycle.REJECTED, LearningLifecycle.FAILED},
    LearningLifecycle.PRACTICING: {LearningLifecycle.ASSESSING, LearningLifecycle.FAILED},
    LearningLifecycle.ASSESSING: {LearningLifecycle.VALIDATING, LearningLifecycle.FAILED},
    LearningLifecycle.VALIDATING: {LearningLifecycle.READY_FOR_UPDATE, LearningLifecycle.REJECTED, LearningLifecycle.FAILED},
    LearningLifecycle.READY_FOR_UPDATE: {LearningLifecycle.AWAITING_HUMAN_APPROVAL, LearningLifecycle.FAILED},
    LearningLifecycle.AWAITING_HUMAN_APPROVAL: {LearningLifecycle.UPDATED, LearningLifecycle.REJECTED},
    LearningLifecycle.UPDATED: set(),
    LearningLifecycle.REJECTED: set(),
    LearningLifecycle.FAILED: set(),
}


class LearningStateMachine:
    def __init__(self) -> None:
        self.state = LearningLifecycle.IDENTIFIED
        self.history = [LearningLifecycle.IDENTIFIED]

    def move(self, target: LearningLifecycle) -> LearningLifecycle:
        if target not in _NEXT[self.state]:
            raise ValueError(f"Invalid learning transition: {self.state.value} -> {target.value}")
        self.state = target
        self.history.append(target)
        return target
