from __future__ import annotations

from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryProvider:
    def store(self, value: Any, memory_type: MemoryType = MemoryType.WORKING, metadata: dict[str, Any] | None = None) -> UUID:
        raise NotImplementedError

    def retrieve(self, memory_id: UUID) -> dict[str, Any] | None:
        raise NotImplementedError

    def search(self, query: str, memory_type: MemoryType | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def delete(self, memory_id: UUID) -> bool:
        raise NotImplementedError


class InMemoryMemoryProvider(MemoryProvider):
    def __init__(self) -> None:
        self._items: dict[UUID, dict[str, Any]] = {}

    def store(self, value: Any, memory_type: MemoryType = MemoryType.WORKING, metadata: dict[str, Any] | None = None) -> UUID:
        memory_id = uuid4()
        self._items[memory_id] = {"id": memory_id, "value": value, "type": memory_type, "metadata": metadata or {}}
        return memory_id

    def retrieve(self, memory_id: UUID) -> dict[str, Any] | None:
        return self._items.get(memory_id)

    def search(self, query: str, memory_type: MemoryType | None = None) -> list[dict[str, Any]]:
        needle = query.casefold()
        return [item for item in self._items.values() if (memory_type is None or item["type"] == memory_type) and needle in str(item["value"]).casefold()]

    def delete(self, memory_id: UUID) -> bool:
        return self._items.pop(memory_id, None) is not None
