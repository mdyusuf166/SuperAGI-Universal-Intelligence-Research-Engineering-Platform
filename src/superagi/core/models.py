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


class TaskStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class AgentStatus(str, Enum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class EventType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_QUEUED = "task_queued"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    PLAN_CREATED = "plan_created"
    PLAN_STARTED = "plan_started"
    PLAN_COMPLETED = "plan_completed"
    PLAN_FAILED = "plan_failed"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    TOOL_FAILED = "tool_failed"
    MEMORY_STORED = "memory_stored"
    MEMORY_RETRIEVED = "memory_retrieved"
    VERIFICATION_STARTED = "verification_started"
    VERIFICATION_COMPLETED = "verification_completed"
    MOLECULE_VALIDATED = "molecule_validated"
    MOLECULAR_DESCRIPTORS_CALCULATED = "molecular_descriptors_calculated"
    FINGERPRINT_GENERATED = "fingerprint_generated"
    SIMILARITY_CALCULATED = "similarity_calculated"
    DNA_ANALYZED = "dna_analyzed"
    PREDICTION_REQUESTED = "prediction_requested"
    PREDICTION_COMPLETED = "prediction_completed"
    PREDICTION_FAILED = "prediction_failed"
    CANDIDATE_RANKED = "candidate_ranked"


class Task(IdentityModel):
    description: str = Field(min_length=1)
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.CREATED
    result: "AgentResult | None" = None
    error: str | None = None


class AgentContext(IdentityModel):
    task_id: UUID
    values: dict[str, Any] = Field(default_factory=dict)


class AgentMetadata(IdentityModel):
    name: str = Field(min_length=1)
    description: str = ""
    version: str = "0.1.0"
    capabilities: tuple[str, ...] = ()
    required_tools: tuple[str, ...] = ()
    risk_level: str = "low"


class PlanStep(StrictModel):
    step_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    dependencies: tuple[str, ...] = ()
    status: ExecutionStatus = ExecutionStatus.PENDING
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=0, ge=0)
    timeout: float | None = Field(default=None, gt=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Plan(IdentityModel):
    task_id: UUID
    steps: list[PlanStep] = Field(default_factory=list)


class ExecutionStep(IdentityModel):
    task_id: UUID
    step_type: str
    status: ExecutionStatus = ExecutionStatus.PENDING
    agent_id: UUID | None = None
    tool_id: UUID | None = None
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_ms: float | None = None


class AgentResult(IdentityModel):
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    summary: str = ""
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    limitations: list[str] = Field(default_factory=list)


class ToolResult(IdentityModel):
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class Event(StrictModel):
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    timestamp: datetime = Field(default_factory=utc_now)
    task_id: UUID
    agent_id: UUID | None = None
    tool_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
