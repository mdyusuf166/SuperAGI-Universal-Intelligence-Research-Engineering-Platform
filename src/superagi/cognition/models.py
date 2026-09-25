"""Typed records for one bounded cognitive cycle."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CM(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CognitiveLifecycle(str, Enum):
    CREATED = "CREATED"
    INGESTING = "INGESTING"
    CONTEXT_READY = "CONTEXT_READY"
    REASONING = "REASONING"
    SIMULATING = "SIMULATING"
    PREDICTING = "PREDICTING"
    PLANNING = "PLANNING"
    DECISION_REVIEW = "DECISION_REVIEW"
    ACTION_PROPOSED = "ACTION_PROPOSED"
    AWAITING_HUMAN_APPROVAL = "AWAITING_HUMAN_APPROVAL"
    OBSERVING = "OBSERVING"
    EVALUATING = "EVALUATING"
    LEARNING = "LEARNING"
    EVOLUTION_REVIEW = "EVOLUTION_REVIEW"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class EpistemicStatus(str, Enum):
    OBSERVED = "OBSERVED"
    EVIDENCED = "EVIDENCED"
    INFERRED = "INFERRED"
    HYPOTHESIZED = "HYPOTHESIZED"
    PREDICTED = "PREDICTED"
    SIMULATED = "SIMULATED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"


class ObservationSource(str, Enum):
    USER_INPUT = "USER_INPUT"
    MEMORY = "MEMORY"
    RESEARCH_ARTIFACT = "RESEARCH_ARTIFACT"
    WORLD_MODEL = "WORLD_MODEL"
    SIMULATION = "SIMULATION"
    PREDICTION = "PREDICTION"
    EXTERNAL_RESULT = "EXTERNAL_RESULT"


class ObservationType(str, Enum):
    TEXT = "TEXT"
    NUMERIC = "NUMERIC"
    EVENT = "EVENT"
    STATE = "STATE"


class OutcomeStatus(str, Enum):
    OBSERVED_SUCCESS = "OBSERVED_SUCCESS"
    OBSERVED_FAILURE = "OBSERVED_FAILURE"
    OBSERVED_PARTIAL = "OBSERVED_PARTIAL"
    UNKNOWN_OUTCOME = "UNKNOWN_OUTCOME"
    NOT_EXECUTED = "NOT_EXECUTED"


class ActionStatus(str, Enum):
    PROPOSAL = "PROPOSAL"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"


class CognitiveEventName(str, Enum):
    CYCLE_STARTED = "CYCLE_STARTED"
    OBSERVATION_INGESTED = "OBSERVATION_INGESTED"
    CONTEXT_BUILT = "CONTEXT_BUILT"
    REASONING_COMPLETED = "REASONING_COMPLETED"
    SIMULATION_COMPLETED = "SIMULATION_COMPLETED"
    PREDICTION_COMPLETED = "PREDICTION_COMPLETED"
    PLAN_CREATED = "PLAN_CREATED"
    DECISION_PROPOSED = "DECISION_PROPOSED"
    ACTION_PROPOSED = "ACTION_PROPOSED"
    SAFETY_REVIEWED = "SAFETY_REVIEWED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    OBSERVATION_RECEIVED = "OBSERVATION_RECEIVED"
    EVALUATION_COMPLETED = "EVALUATION_COMPLETED"
    LEARNING_PROPOSED = "LEARNING_PROPOSED"
    EVOLUTION_PROPOSED = "EVOLUTION_PROPOSED"
    CYCLE_COMPLETED = "CYCLE_COMPLETED"
    CYCLE_FAILED = "CYCLE_FAILED"


class ProvenanceNote(CM):
    source: str | None = None
    status: str = "MISSING"
    ref_id: str = ""


class NumericSignal(CM):
    name: str
    value: float


class Observation(CM):
    id: UUID = Field(default_factory=uuid4)
    statement: str = Field(min_length=1)
    source_kind: ObservationSource
    observation_type: ObservationType = ObservationType.TEXT
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    evidence_refs: list[str] = Field(default_factory=list)
    provenance: ProvenanceNote = Field(default_factory=ProvenanceNote)
    created_at: datetime = Field(default_factory=utc_now)


class IngestionResult(CM):
    observations: list[Observation]
    rejected: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ContextItem(CM):
    kind: str
    label: str
    epistemic: EpistemicStatus
    ref_id: str = ""
    provenance: ProvenanceNote = Field(default_factory=ProvenanceNote)


class CognitiveContext(CM):
    memories: list[ContextItem] = Field(default_factory=list)
    evidence: list[ContextItem] = Field(default_factory=list)
    entities: list[ContextItem] = Field(default_factory=list)
    relations: list[ContextItem] = Field(default_factory=list)
    goals: list[ContextItem] = Field(default_factory=list)
    constraints: list[ContextItem] = Field(default_factory=list)
    research_notes: list[ContextItem] = Field(default_factory=list)
    bound: int
    truncated: bool = False
    limitations: list[str] = Field(default_factory=list)


class Claim(CM):
    statement: str
    epistemic: EpistemicStatus
    evidence_refs: list[str] = Field(default_factory=list)


class ReasoningResult(CM):
    claims: list[Claim] = Field(default_factory=list)
    inferences: list[Claim] = Field(default_factory=list)
    unknowns: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence: float | None = None
    confidence_basis: str = "No confidence was supplied."
    limitations: list[str] = Field(default_factory=list)


class CognitiveSimulationResult(CM):
    status: str
    classification: str
    epistemic: EpistemicStatus
    values: list[NumericSignal] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class CognitivePredictionResult(CM):
    method: str
    horizon: int
    values: list[float] = Field(default_factory=list)
    epistemic: EpistemicStatus
    confidence: float | None = None
    confidence_basis: str
    measured_accuracy: str = "NOT_EVALUABLE"
    uncertainty: str
    evidence_refs: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class PlanProposal(CM):
    status: str = "PROPOSAL"
    steps: list[str] = Field(default_factory=list)
    feasible: bool = False
    executed: bool = False
    basis: str
    limitations: list[str] = Field(default_factory=list)


class DecisionView(CM):
    question: str
    options: list[str]
    criteria: list[str]
    evidence: list[str]
    assumptions: list[str]
    risks: list[str]
    tradeoffs: str
    uncertainty: str
    approved: bool = False
    status: str = "PROPOSAL"
    human_approval_required: bool = True
    executed: bool = False


class ActionProposal(CM):
    id: UUID = Field(default_factory=uuid4)
    action: str
    reason: str
    evidence: list[str] = Field(default_factory=list)
    risk: str
    constraints: list[str] = Field(default_factory=list)
    approval_required: bool = True
    approval_status: ActionStatus = ActionStatus.PROPOSAL
    executed: bool = False
    provenance: ProvenanceNote = Field(default_factory=ProvenanceNote)


class SafetyFinding(CM):
    policy: str
    allowed: bool
    reasons: list[str] = Field(default_factory=list)
    mode: str


class SafetyReport(CM):
    allowed: bool
    findings: list[SafetyFinding]
    executed: bool = False


class FeedbackRecord(CM):
    status: OutcomeStatus
    statement: str
    synthetic: bool = True
    limitations: list[str] = Field(default_factory=list)


class EvalItem(CM):
    name: str
    status: str
    detail: str


class EvaluationReport(CM):
    items: list[EvalItem]
    limitations: list[str] = Field(default_factory=list)


class LearningUpdateProposal(CM):
    gap: str
    statement: str
    applied: bool = False
    limitations: list[str] = Field(default_factory=list)


class EvolutionRecord(CM):
    gap: str
    lifecycle: str
    change: str
    applied: bool = False
    human_approval: bool = False
    limitations: list[str] = Field(default_factory=list)


class DomainContribution(CM):
    domain: str
    arcs: list[str]
    note: str
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN


class CognitiveDomainResult(CM):
    contributions: list[DomainContribution]
    selected_winner: str | None = None
    conflict: str | None = None
    basis: str


class CycleProvenance(CM):
    cycle: ProvenanceNote
    task: ProvenanceNote
    observation: ProvenanceNote
    memory: ProvenanceNote
    evidence: ProvenanceNote
    world_model: ProvenanceNote
    reasoning: ProvenanceNote
    simulation: ProvenanceNote
    prediction: ProvenanceNote
    plan: ProvenanceNote
    decision: ProvenanceNote
    action_proposal: ProvenanceNote
    evaluation: ProvenanceNote
    learning_proposal: ProvenanceNote
    evolution_proposal: ProvenanceNote


class CognitiveEventRecord(CM):
    name: CognitiveEventName
    summary: str
    created_at: datetime = Field(default_factory=utc_now)


class CycleRequest(CM):
    goal: str = Field(min_length=1)
    observations: list[Observation] = Field(default_factory=list)
    source: str | None = None
    domains: list[str] = Field(default_factory=list)
    question: str | None = None
    series: list[float] = Field(default_factory=list)
    simulate: bool = False
    predict: bool = False
    signals: list[NumericSignal] = Field(default_factory=list)
    deltas: list[NumericSignal] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    outcome: OutcomeStatus | None = None
    outcome_statement: str = ""
    approval_required: bool = True
    human_approved: bool = False
    research_notes: list[str] = Field(default_factory=list)


class CognitiveState(CM):
    cycle_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    goal: str
    lifecycle: CognitiveLifecycle = CognitiveLifecycle.CREATED
    history: list[CognitiveLifecycle] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    memory_refs: list[str] = Field(default_factory=list)
    world_model_refs: list[str] = Field(default_factory=list)
    context: CognitiveContext | None = None
    reasoning_result: ReasoningResult | None = None
    simulation_result: CognitiveSimulationResult | None = None
    prediction_result: CognitivePredictionResult | None = None
    plan_result: PlanProposal | None = None
    decision_result: DecisionView | None = None
    action_proposals: list[ActionProposal] = Field(default_factory=list)
    evaluation: EvaluationReport | None = None
    learning_update: LearningUpdateProposal | None = None
    evolution_proposal: EvolutionRecord | None = None
    domain_result: CognitiveDomainResult | None = None
    feedback: FeedbackRecord | None = None
    provenance: CycleProvenance
    safety_status: SafetyReport | None = None
    events: list[CognitiveEventRecord] = Field(default_factory=list)
    failure: str | None = None
    executed: bool = False
    limitations: list[str] = Field(default_factory=list)
