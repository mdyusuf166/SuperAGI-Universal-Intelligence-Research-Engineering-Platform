from __future__ import annotations

import re
from uuid import UUID

from ..models import MemoryRecord, MemoryType
from .base import MemoryProvider


def normalize_content(content: str) -> str:
    return re.sub(r"\s+", " ", content.strip().casefold())


class InMemoryMemoryProvider(MemoryProvider):
    def __init__(self) -> None:
        self._records: dict[UUID, MemoryRecord] = {}
        self._normalized: dict[tuple[str, str | None], UUID] = {}

    def store(self, record: MemoryRecord) -> MemoryRecord:
        key = (normalize_content(record.content), record.source_id)
        duplicate = self._normalized.get(key)
        if duplicate is not None:
            return self._records[duplicate]
        self._records[record.id] = record
        self._normalized[key] = record.id
        return record

    def retrieve(self, memory_id: UUID) -> MemoryRecord | None:
        return self._records.get(memory_id)

    def search(self, query: str, *, memory_type: MemoryType | None = None, source: str | None = None, min_confidence: float | None = None) -> list[MemoryRecord]:
        terms = set(re.findall(r"[\w-]+", normalize_content(query)))
        candidates = []
        for record in self._records.values():
            if memory_type and record.memory_type is not memory_type:
                continue
            if source and record.source != source:
                continue
            if min_confidence is not None and record.confidence < min_confidence:
                continue
            content_terms = set(re.findall(r"[\w-]+", normalize_content(record.content)))
            if not terms or terms & content_terms:
                candidates.append((len(terms & content_terms), record))
        return [record for _, record in sorted(candidates, key=lambda item: (-item[0], str(item[1].id)))]

    def delete(self, memory_id: UUID) -> bool:
        record = self._records.pop(memory_id, None)
        if record is None:
            return False
        self._normalized.pop((normalize_content(record.content), record.source_id), None)
        return True
