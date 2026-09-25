"""Deterministic capability routing. Multiple matches stay unresolved."""

from __future__ import annotations

from .models import CognitiveDomainResult, DomainContribution, EpistemicStatus

_RULES = (
    ("biomedical", ("biomedical", "molecule", "gene"), ("ARC-04",)),
    ("robotics", ("robot", "navigation"), ("ARC-07", "ARC-15")),
    ("engineering", ("engineering", "design", "circuit"), ("ARC-13", "ARC-15")),
    ("education", ("student", "study", "learn"), ("ARC-11",)),
    ("personal", ("personal goal", "personal planning"), ("ARC-10", "ARC-14")),
    ("collaboration", ("collaboration", "team decision"), ("ARC-14",)),
    ("world_model", ("world model", "knowledge graph"), ("ARC-16",)),
    ("research", ("research", "hypothesis", "science"), ("ARC-03", "ARC-12")),
    ("cybersecurity", ("cyber", "defensive log"), ("ARC-08",)),
    ("quantum", ("quantum",), ("ARC-06",)),
    ("neuro", ("neuro", "spiking"), ("ARC-05",)),
)


class CognitiveRouter:
    def route(self, goal: str, domains: list[str] | None = None) -> CognitiveDomainResult:
        requested = {item.casefold() for item in domains or []}
        folded = goal.casefold()
        matched: list[tuple[str, tuple[str, ...]]] = []
        for name, words, arcs in _RULES:
            if name in requested or any(word in folded for word in words):
                matched.append((name, arcs))
        if not matched:
            matched.append(("orchestration", ("ARC-09",)))
            return CognitiveDomainResult(contributions=[DomainContribution(domain="orchestration", arcs=["ARC-09"], note="No single domain keyword matched. ARC-09 remains available for computational orchestration.", epistemic=EpistemicStatus.UNKNOWN)], selected_winner=None, conflict=None, basis="No domain keyword matched. No winner was selected.")
        contributions = [DomainContribution(domain=name, arcs=list(arcs), note=f"Capability descriptor {name} matched the goal text or the caller domain list.", epistemic=EpistemicStatus.UNKNOWN) for name, arcs in matched]
        if len(contributions) == 1:
            return CognitiveDomainResult(contributions=contributions, selected_winner=contributions[0].domain, conflict=None, basis="Single capability match. This is not a scored ranking.")
        return CognitiveDomainResult(contributions=contributions, selected_winner=None, conflict="Multiple domains matched. No domain winner was selected.", basis="All matching capability descriptors are retained.")
