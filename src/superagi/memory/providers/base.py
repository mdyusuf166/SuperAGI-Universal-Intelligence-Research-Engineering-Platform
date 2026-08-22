from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from ..models import MemoryRecord, MemoryType


class MemoryProvider(ABC):
    @abstractmethod
    def store(self, record: MemoryRecord) -> MemoryRecord:
        """Store a memory record."""

    @abstractmethod
    def retrieve(self, memory_id: UUID) -> MemoryRecord | None:
        """Retrieve a memory record by ID."""

    @abstractmethod
    def search(self, query: str, *, memory_type: MemoryType | None = None, source: str | None = None, min_confidence: float | None = None) -> list[MemoryRecord]:
        """Search records using deterministic filters and lexical matching."""

    @abstractmethod
    def delete(self, memory_id: UUID) -> bool:
        """Delete a memory record."""


class VectorMemoryProvider(MemoryProvider):
    """Future vector-backed provider boundary; embeddings are not ARC-02."""


class GraphMemoryProvider(MemoryProvider):
    """Future graph-backed memory boundary."""


class PostgresMemoryProvider(MemoryProvider):
    """Future PostgreSQL-backed provider boundary."""


class RedisMemoryProvider(MemoryProvider):
    """Future Redis-backed provider boundary."""
