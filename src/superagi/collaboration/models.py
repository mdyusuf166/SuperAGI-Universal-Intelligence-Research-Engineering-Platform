"""Typed collaboration records. Personal attributes are only those a person supplies."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CM(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InteractionMode(str, Enum):
    HUMAN_ONLY = "HUMAN_ONLY"
    AI_ASSISTED = "AI_ASSISTED"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    SIMULATION_ONLY = "SIMULATION_ONLY"


class ConsentState(str, Enum):
    GRANTED = "granted"
    DENIED = "denied"
    ABSENT = "absent"


class ReviewSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ArtifactStatus(str, Enum):
    RECOMMENDATION = "RECOMMENDATION"
    DECISION = "DECISION"
    PROPOSAL = "PROPOSAL"
    DRAFT = "DRAFT"
    APPROVED_ACTION = "APPROVED_ACTION"


class Consent(CM):
    state: ConsentState = ConsentState.ABSENT
    scope: list[str] = Field(default_factory=list)
    persistent: bool = False


class Person(CM):
    id: UUID = Field(default_factory=uuid4)
    display_name: str
    consent: Consent = Field(default_factory=Consent)


class Preference(CM):
    id: UUID = Field(default_factory=uuid4)
    key: str
    value: str
    source: str = "user-declared"


class CollaborationConstraint(CM):
    id: UUID = Field(default_factory=uuid4)
    kind: str
    limit: str
    source: str = "user"


class ContextItem(CM):
    id: UUID = Field(default_factory=uuid4)
    text: str
    source: str
    kind: str = "user-declared"


class Milestone(CM):
    id: UUID = Field(default_factory=uuid4)
    name: str
    status: str = "PENDING"
    evidence: list[str] = Field(default_factory=list)


class CollaborationGoal(CM):
    id: UUID = Field(default_factory=uuid4)
    statement: str
    priority: int = 0
    status: str = "ACTIVE"
    proposed: bool = False
    parent_id: UUID | None = None
    personal_goal_id: UUID | None = None
    dependencies: list[UUID] = Field(default_factory=list)
    milestones: list[Milestone] = Field(default_factory=list)
    progress_evidence: list[str] = Field(default_factory=list)


class CollaborationTask(CM):
    id: UUID = Field(default_factory=uuid4)
    title: str
    owner: str
    core_task_id: UUID | None = None
    dependencies: list[UUID] = Field(default_factory=list)
    status: str = "PENDING"
    priority: int = 0
    evidence: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    completion_criteria: list[str] = Field(default_factory=list)


class CollaborationProject(CM):
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str = ""
    personal_project_id: UUID | None = None
    status: str = "ACTIVE"


class Role(CM):
    id: UUID = Field(default_factory=uuid4)
    name: str
    participant: str
    responsibilities: list[str] = Field(default_factory=list)
    human_decision_maker: bool = False


class ProvenanceRef(CM):
    id: UUID = Field(default_factory=uuid4)
    source: str
    evidence: list[str] = Field(default_factory=list)
    originating_agent: str
    session_id: UUID | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    related_task: str | None = None
    related_decision: str | None = None


class Recommendation(CM):
    id: UUID = Field(default_factory=uuid4)
    text: str
    basis: str
    evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    uncertainty: str = "Caller-supplied scores are not objective correctness."
    limitations: list[str] = Field(default_factory=list)
    alternatives: list[str] = Field(default_factory=list)
    status: ArtifactStatus = ArtifactStatus.RECOMMENDATION
    human_approval_required: bool = True


class Decision(CM):
    id: UUID = Field(default_factory=uuid4)
    question: str
    options: list[str] = Field(default_factory=list)
    criteria: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    tradeoffs: str = ""
    recommendation_id: UUID | None = None
    uncertainty: str = "The human remains the decision maker."
    human_approval_required: bool = True
    status: str = "PROPOSAL"
    approved: bool = False


class ActionProposal(CM):
    id: UUID = Field(default_factory=uuid4)
    description: str
    status: ArtifactStatus = ArtifactStatus.DRAFT
    executed: bool = False


class ReviewFinding(CM):
    category: str
    message: str
    severity: ReviewSeverity


class Claim(CM):
    topic: str
    claim: str
    source: str
    kind: str = "UNKNOWN"


class ConflictItem(CM):
    topic: str
    claims: list[str] = Field(default_factory=list)
    resolved: bool = False


class CollaborationSession(CM):
    id: UUID = Field(default_factory=uuid4)
    objective: str
    mode: InteractionMode = InteractionMode.AI_ASSISTED
    participants: list[str] = Field(default_factory=list)
    roles: list[Role] = Field(default_factory=list)
    context: list[ContextItem] = Field(default_factory=list)
    goals: list[CollaborationGoal] = Field(default_factory=list)
    tasks: list[CollaborationTask] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    decisions: list[Decision] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    conflicts: list[ConflictItem] = Field(default_factory=list)
    safety_state: str = "ASSISTANCE_ONLY"


MAX_CONTEXT_ITEMS = 8
MAX_SESSION_ITEMS = 12
