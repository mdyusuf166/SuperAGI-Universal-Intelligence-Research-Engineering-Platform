"""Consent and request safety. This layer does not infer private attributes."""

from __future__ import annotations

from .models import Consent, ConsentState, Preference

_BLOCKED = (
    "autonomous irreversible",
    "irreversible action",
    "unauthorized external",
    "hidden personal",
    "infer health",
    "health condition",
    "medical diagnosis",
    "psychological diagnosis",
    "political preference",
    "political affiliation",
    "infer race",
    "infer religion",
    "infer ethnicity",
    "protected characteristic",
    "api key",
    "password",
    "credential",
    "dangerous physical",
    "autonomous deployment",
    "active exam",
    "cheat",
    "submit for me",
    "write my exam",
)

_FORBIDDEN_PREFERENCE_KEYS = {
    "health",
    "diagnosis",
    "political_preference",
    "race",
    "religion",
    "ethnicity",
    "sexual_orientation",
}


class ConsentGate:
    def persistent_allowed(self, consent: Consent | None) -> bool:
        if consent is None or consent.state != ConsentState.GRANTED or not consent.persistent:
            return False
        return "persistent" in consent.scope

    def session_allowed(self, consent: Consent | None) -> bool:
        if consent is None or consent.state == ConsentState.ABSENT:
            return True
        return consent.state == ConsentState.GRANTED


class SafetyPolicy:
    def assess(self, text: str) -> dict:
        folded = text.casefold()
        hits = [item for item in _BLOCKED if item in folded]
        return {"allowed": not hits, "mode": "ASSISTANCE_ONLY", "reasons": hits, "executed": False}

    def check_preference(self, preference: Preference) -> None:
        if preference.key.casefold() in _FORBIDDEN_PREFERENCE_KEYS:
            raise PermissionError("Sensitive attributes are not stored or inferred")
        if preference.source != "user-declared":
            raise PermissionError("Preferences must be user-declared")
