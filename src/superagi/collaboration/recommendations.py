"""Deterministic recommendations. Nothing here becomes an action on its own."""

from __future__ import annotations

from .models import ActionProposal, ArtifactStatus, Recommendation


class RecommendationEngine:
    def recommend(self, options: list[dict]) -> Recommendation:
        if not options:
            return Recommendation(text="No option was supplied.", basis="No caller-supplied options.", confidence=0.0, limitations=["No recommendation can be formed without explicit options."], alternatives=[])
        scored = []
        for option in options:
            criteria = option.get("criteria", {})
            scored.append((sum(criteria.values()), option["name"], option))
        scored.sort(key=lambda item: (item[0], item[1]))
        _score, name, best = scored[0]
        alternatives = [item[1] for item in scored[1:]]
        return Recommendation(
            text=name,
            basis="Lowest explicit criterion sum, then name.",
            evidence=list(best.get("evidence", [])),
            assumptions=list(best.get("assumptions", [])),
            confidence=0.4,
            uncertainty="Scores are caller-supplied and are not objective correctness.",
            limitations=["This is a recommendation, not an approved action."],
            alternatives=alternatives,
            status=ArtifactStatus.RECOMMENDATION,
            human_approval_required=True,
        )

    def draft_action(self, recommendation: Recommendation) -> ActionProposal:
        return ActionProposal(description=recommendation.text, status=ArtifactStatus.DRAFT, executed=False)
