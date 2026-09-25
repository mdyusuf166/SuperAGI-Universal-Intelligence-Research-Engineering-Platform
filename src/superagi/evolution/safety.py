"""Safety gate for simulation and evolution requests."""

from __future__ import annotations

_BLOCKED = (
    "modify source code",
    "autonomous deployment",
    "credential",
    "api key",
    "password",
    "unauthorized external",
    "irreversible",
    "dangerous physical",
    "clinical decision",
    "financial execution",
    "weapon",
    "malware",
    "exploit",
    "permission escalation",
    "hidden personal",
)


class EvolutionSafetyPolicy:
    def assess(self, text: str) -> dict:
        folded = text.casefold()
        hits = [item for item in _BLOCKED if item in folded]
        return {"allowed": not hits, "mode": "SIMULATION_ONLY", "reasons": hits, "executed": False}
