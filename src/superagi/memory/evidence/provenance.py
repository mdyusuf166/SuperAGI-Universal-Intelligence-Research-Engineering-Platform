from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class ProvenanceStage(str, Enum):
    SOURCE = "source"
    DOCUMENT = "document"
    CHUNK = "chunk"
    CLAIM = "claim"
    EVIDENCE = "evidence"
    AGENT_RESULT = "agent_result"


class ProvenanceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID = Field(default_factory=uuid4)
    stage: ProvenanceStage
    producer: str
    source: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    operation: str
    input_references: tuple[str, ...] = ()
    output_references: tuple[str, ...] = ()
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProvenanceStore:
    def __init__(self) -> None:
        self.records: list[ProvenanceRecord] = []

    def add(self, record: ProvenanceRecord) -> ProvenanceRecord:
        self.records.append(record)
        return record

    def chain(self, reference: str) -> list[ProvenanceRecord]:
        return [record for record in self.records if reference in record.input_references or reference in record.output_references]
