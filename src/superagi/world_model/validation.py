"""Safety checks and structural validation issues."""

from __future__ import annotations

_BLOCKED = (
    "hidden personal",
    "sensitive attribute",
    "unauthorized surveillance",
    "credential",
    "api key",
    "password",
    "unauthorized external",
    "clinical decision",
    "financial execution",
    "weapon",
    "malware",
    "exploit",
    "autonomous physical",
)


class WorldModelSafetyPolicy:
    def assess(self, text: str) -> dict:
        folded = text.casefold()
        hits = [item for item in _BLOCKED if item in folded]
        return {"allowed": not hits, "reasons": hits, "executed": False, "mode": "MODEL_ONLY"}

    def guard(self, text: str) -> None:
        report = self.assess(text)
        if not report["allowed"]:
            raise PermissionError("World model safety policy rejected the request")
