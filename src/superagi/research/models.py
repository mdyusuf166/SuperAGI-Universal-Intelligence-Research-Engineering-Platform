from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ResearchModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class ResearchQuestion(ResearchModel):
    id: UUID = Field(default_factory=uuid4)
    question: str = Field(min_length=1)
    domain: str = "general"
    objectives: tuple[str, ...] = ()
    subquestions: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    created_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ResearchRunStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchRun(ResearchModel):
    id: UUID = Field(default_factory=uuid4)
    question_id: UUID
    plan_id: UUID | None = None
    status: ResearchRunStatus = ResearchRunStatus.CREATED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    stage_results: dict[str, Any] = Field(default_factory=dict)
    verification: Any | None = None
    metrics: dict[str, float] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
