from __future__ import annotations

import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class EvidenceStatus(str, Enum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially_supported"
    UNSUPPORTED = "unsupported"
    CONTRADICTED = "contradicted"
    UNKNOWN = "unknown"


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    claim: str = Field(min_length=1)
    source: str
    source_type: str
    source_id: str | None = None
    excerpt: str = ""
    confidence: float = Field(default=0.5, ge=0, le=1)
    status: EvidenceStatus = EvidenceStatus.UNKNOWN
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceStore:
    def __init__(self) -> None:
        self._items: dict[UUID, Evidence] = {}
        self._claims: dict[str, list[UUID]] = {}

    def add(self, evidence: Evidence) -> Evidence:
        self._items[evidence.id] = evidence
        self._claims.setdefault(evidence.claim.casefold(), []).append(evidence.id)
        return evidence

    def get(self, evidence_id: UUID) -> Evidence | None:
        return self._items.get(evidence_id)

    def search(self, query: str) -> list[Evidence]:
        terms = set(re.findall(r"[\w-]+", query.casefold()))
        return [item for item in self._items.values() if terms & set(re.findall(r"[\w-]+", f"{item.claim} {item.excerpt}".casefold()))]

    def link_to_claim(self, claim: str) -> list[Evidence]:
        return [self._items[item_id] for item_id in self._claims.get(claim.casefold(), [])]
