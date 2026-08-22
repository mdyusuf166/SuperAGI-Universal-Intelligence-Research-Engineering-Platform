from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class IdentityModel(StrictModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    RESEARCH = "research"
    EXPERIMENTAL = "experimental"


class SourceType(str, Enum):
    USER = "user"
    PAPER = "paper"
    BOOK = "book"
    WEB = "web"
    DATASET = "dataset"
    CODE = "code"
    EXPERIMENT = "experiment"
    SYSTEM = "system"
    AGENT = "agent"


class MemoryRecord(IdentityModel):
    content: str = Field(min_length=1)
    memory_type: MemoryType = MemoryType.WORKING
    source: str = "system"
    source_id: str | None = None
    importance: float = Field(default=0.5, ge=0, le=1)
    confidence: float = Field(default=0.5, ge=0, le=1)
    tags: tuple[str, ...] = ()


class Document(IdentityModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    source: str
    source_type: SourceType
    authors: tuple[str, ...] = ()


class DocumentChunk(IdentityModel):
    document_id: UUID
    content: str = Field(min_length=1)
    position: int = Field(ge=0)
    token_estimate: int = Field(ge=1)
