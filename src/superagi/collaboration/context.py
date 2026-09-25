"""Bounded collaboration context. Personal text is stored only with persistent consent."""

from __future__ import annotations

from superagi.personal.services import PersonalMemoryService

from .models import MAX_CONTEXT_ITEMS, Consent, ContextItem
from .safety import ConsentGate


class ContextService:
    def __init__(self, memory=None, personal: PersonalMemoryService | None = None) -> None:
        self.memory = memory
        self.personal = personal
        self.gate = ConsentGate()

    def build(self, items: list[ContextItem], consent: Consent | None) -> dict:
        kept = list(items[:MAX_CONTEXT_ITEMS])
        return {"items": kept, "truncated": len(items) > MAX_CONTEXT_ITEMS, "persisted": False, "mode": "session-only"}

    def store(self, items: list[ContextItem], consent: Consent | None) -> dict:
        built = self.build(items, consent)
        if not self.gate.persistent_allowed(consent):
            built["reason"] = "consent absent, denied, or limited to the session"
            return built
        if self.personal is None or self.memory is None:
            built["reason"] = "no memory service was provided"
            return built
        self.personal.allow_memory()
        ids = []
        for item in built["items"]:
            record = self.personal.remember(item.text, category="collaboration-context")
            ids.append(str(record.id))
        built["persisted"] = True
        built["mode"] = "persistent"
        built["memory_ids"] = ids
        built["reason"] = "persistent consent granted"
        return built

    def recall(self, query: str, limit: int = 5) -> list:
        if self.memory is None:
            return []
        return list(self.memory.search(query, limit=limit))[:limit]
