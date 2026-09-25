"""Validated cognitive lifecycle. Invalid transitions fail explicitly."""

from __future__ import annotations

from .models import CognitiveLifecycle

_NEXT = {
    CognitiveLifecycle.CREATED: {CognitiveLifecycle.INGESTING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.INGESTING: {CognitiveLifecycle.CONTEXT_READY, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.CONTEXT_READY: {CognitiveLifecycle.REASONING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.REASONING: {CognitiveLifecycle.SIMULATING, CognitiveLifecycle.PREDICTING, CognitiveLifecycle.PLANNING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.SIMULATING: {CognitiveLifecycle.PREDICTING, CognitiveLifecycle.PLANNING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.PREDICTING: {CognitiveLifecycle.PLANNING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.PLANNING: {CognitiveLifecycle.DECISION_REVIEW, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.DECISION_REVIEW: {CognitiveLifecycle.ACTION_PROPOSED, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.ACTION_PROPOSED: {CognitiveLifecycle.AWAITING_HUMAN_APPROVAL, CognitiveLifecycle.OBSERVING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.AWAITING_HUMAN_APPROVAL: {CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.OBSERVING: {CognitiveLifecycle.EVALUATING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.EVALUATING: {CognitiveLifecycle.LEARNING, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.LEARNING: {CognitiveLifecycle.EVOLUTION_REVIEW, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.EVOLUTION_REVIEW: {CognitiveLifecycle.COMPLETED, CognitiveLifecycle.FAILED, CognitiveLifecycle.CANCELLED},
    CognitiveLifecycle.COMPLETED: set(),
    CognitiveLifecycle.FAILED: set(),
    CognitiveLifecycle.CANCELLED: set(),
}


class CognitiveStateMachine:
    def __init__(self) -> None:
        self.state = CognitiveLifecycle.CREATED
        self.history = [CognitiveLifecycle.CREATED]

    def move(self, target: CognitiveLifecycle) -> CognitiveLifecycle:
        if target not in _NEXT[self.state]:
            raise ValueError(f"Invalid transition: {self.state.value} -> {target.value}")
        self.state = target
        self.history.append(target)
        return self.state

    def cancel(self) -> CognitiveLifecycle:
        return self.move(CognitiveLifecycle.CANCELLED)

    def fail(self) -> CognitiveLifecycle:
        return self.move(CognitiveLifecycle.FAILED)
