"""ARC-09 coordination. Conflicts stay visible and are not reduced to one winner."""

from __future__ import annotations

from superagi.memory import UniversalMemory
from superagi.orchestration import IntelligenceRequest, UniversalIntelligenceCoordinator

from .models import Claim, ConflictItem


class CoordinationService:
    def discover(self, registry, capabilities: list[str], domain: str | None = None) -> list:
        if registry is None:
            return []
        return list(registry.discover(capabilities, domain=domain))

    def claim_conflicts(self, claims: list[Claim]) -> list[ConflictItem]:
        grouped: dict[str, list[str]] = {}
        for claim in claims:
            grouped.setdefault(claim.topic, [])
            if claim.claim not in grouped[claim.topic]:
                grouped[claim.topic].append(claim.claim)
        return [ConflictItem(topic=topic, claims=values, resolved=False) for topic, values in grouped.items() if len(values) > 1]

    def coordinate(self, objective: str, registry, capabilities: list[str]) -> dict:
        discovered = self.discover(registry, capabilities)
        conflicts: list[ConflictItem] = []
        orchestration_conflicts = []
        status = "UNAVAILABLE"
        if registry is not None:
            report = UniversalIntelligenceCoordinator(registry, memory=UniversalMemory()).solve(IntelligenceRequest(goal=objective, capabilities=list(capabilities), execution_mode="COMPUTATIONAL"))
            status = report.status
            orchestration_conflicts = [{"description": item.description, "severity": item.severity, "resolution_status": item.resolution_status} for item in report.conflicts]
        return {
            "agents": [agent.name for agent in discovered],
            "status": status,
            "conflicts": conflicts,
            "orchestration_conflicts": orchestration_conflicts,
            "selected_conflict_winner": None,
            "executed_external": False,
        }
