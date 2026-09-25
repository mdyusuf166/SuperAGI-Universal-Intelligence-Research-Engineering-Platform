"""Transparent decision support. A recommendation is not a decision."""

from __future__ import annotations

from .models import Decision
from .recommendations import RecommendationEngine


class DecisionSupport:
    def __init__(self, engine: RecommendationEngine | None = None) -> None:
        self.engine = engine or RecommendationEngine()

    def prepare(self, *, question: str, options: list[dict], criteria: list[str], evidence: list[str], assumptions: list[str], risks: list[str], tradeoffs: str) -> dict:
        recommendation = self.engine.recommend(options)
        decision = Decision(question=question, options=[option["name"] for option in options], criteria=criteria, evidence=evidence, assumptions=assumptions, risks=risks, tradeoffs=tradeoffs, recommendation_id=recommendation.id, human_approval_required=True, status="PROPOSAL", approved=False)
        return {"decision": decision, "recommendation": recommendation, "kind": "PROPOSAL", "executed": False}

    def approve(self, decision: Decision, *, human: bool) -> Decision:
        if not human:
            raise PermissionError("Only a human can approve a decision")
        decision.approved = True
        decision.status = "DECISION"
        return decision
