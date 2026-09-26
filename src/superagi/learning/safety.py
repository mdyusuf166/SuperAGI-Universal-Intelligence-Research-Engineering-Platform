"""Learning safety policy. It rejects self-modification and unsafe training."""

from __future__ import annotations

_BLOCKED = (
    "unsafe autonomous adaptation",
    "autonomous adaptation",
    "model weight",
    "modify weights",
    "modify source code",
    "source-code modification",
    "permission escalation",
    "change permissions",
    "change safety polic",
    "install software",
    "deploy",
    "credential",
    "api key",
    "password",
    "dangerous physical",
    "physical robot",
    "malware",
    "exploit",
    "weapon",
    "clinical decision",
    "hidden personal",
    "sensitive attribute",
    "infer health",
    "political preference",
)


class LearningSafetyPolicy:
    def assess(self, text: str) -> dict:
        folded = text.casefold()
        hits = [item for item in _BLOCKED if item in folded]
        return {"allowed": not hits, "reasons": hits, "mode": "PROPOSAL_ONLY", "executed": False}

    def guard(self, text: str) -> None:
        if not self.assess(text)["allowed"]:
            raise PermissionError("Learning safety policy rejected the request")
