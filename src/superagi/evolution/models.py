"""Typed records for simulation, prediction, planning, and evolution proposals."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class EM(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BackendStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    MOCK = "MOCK"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class ResultClassification(str, Enum):
    SIMULATION_ONLY = "SIMULATION_ONLY"
    MOCK_SIMULATION = "MOCK_SIMULATION"
    BACKEND_UNAVAILABLE = "BACKEND_UNAVAILABLE"


class EpistemicStatus(str, Enum):
    OBSERVED = "OBSERVED"
    PREDICTED = "PREDICTED"
    INFERRED = "INFERRED"
    UNKNOWN = "UNKNOWN"


class PredictionMethod(str, Enum):
    PERSISTENCE = "persistence"
    MOVING_AVERAGE = "moving_average"
    LINEAR_TREND = "linear_trend"
    RULE_BASED = "rule_based"


class EvolutionLifecycle(str, Enum):
    OBSERVE = "OBSERVE"
    EVALUATE = "EVALUATE"
    IDENTIFY_GAP = "IDENTIFY_GAP"
    PROPOSE_IMPROVEMENT = "PROPOSE_IMPROVEMENT"
    SIMULATE = "SIMULATE"
    VERIFY = "VERIFY"
    REQUEST_HUMAN_APPROVAL = "REQUEST_HUMAN_APPROVAL"
    AWAITING_HUMAN_APPROVAL = "AWAITING_HUMAN_APPROVAL"
    PROPOSAL = "PROPOSAL"


class ReviewSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StateVariable(EM):
    name: str
    value: float


class WorldEntity(EM):
    id: UUID = Field(default_factory=uuid4)
    name: str
    properties: list[StateVariable] = Field(default_factory=list)


class WorldRelation(EM):
    source: str
    kind: str
    target: str


class WorldConstraint(EM):
    kind: str
    limit: str
    source: str = "user"


class WorldEvent(EM):
    name: str
    step: int
    source: str | None = None


class WorldObservation(EM):
    entity: str
    variable: str
    value: float
    status: EpistemicStatus = EpistemicStatus.OBSERVED
    source: str | None = None


class EvolutionGoal(EM):
    id: UUID = Field(default_factory=uuid4)
    statement: str
    external_goal_id: str | None = None


class EvolutionConstraint(EM):
    kind: str
    limit: float
    source: str = "user"


class ProvenanceLink(EM):
    id: UUID = Field(default_factory=uuid4)
    source: str | None = None
    agent: str | None = None
    task: str | None = None
    evidence: list[str] = Field(default_factory=list)
    simulation_id: str | None = None
    prediction_id: str | None = None
    plan_id: str | None = None
    decision_id: str | None = None
    proposal_id: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)
    missing: bool = False


class SimulationState(EM):
    step: int = 0
    variables: list[StateVariable] = Field(default_factory=list)
    terminal: bool = False

    def value(self, name: str) -> float:
        for variable in self.variables:
            if variable.name == name:
                return variable.value
        raise KeyError(name)


class SimulationAction(EM):
    name: str
    deltas: list[StateVariable] = Field(default_factory=list)


class SimulationObservation(EM):
    step: int
    readings: list[StateVariable] = Field(default_factory=list)
    status: EpistemicStatus = EpistemicStatus.OBSERVED


class SimulationTransition(EM):
    step: int
    action: str
    before: list[StateVariable]
    after: list[StateVariable]


class TerminationCondition(EM):
    max_steps: int = 5
    variable: str | None = None
    threshold: float | None = None


class SimulationScenario(EM):
    id: UUID = Field(default_factory=uuid4)
    name: str
    domain: str = "deterministic-mock"
    initial_state: SimulationState
    actions: list[SimulationAction] = Field(default_factory=list)
    termination: TerminationCondition = Field(default_factory=TerminationCondition)
    provenance: ProvenanceLink | None = None


class SimulationResult(EM):
    id: UUID = Field(default_factory=uuid4)
    scenario_id: UUID | None = None
    backend: str
    status: BackendStatus
    classification: ResultClassification
    step_count: int = 0
    trace: list[SimulationState] = Field(default_factory=list)
    transitions: list[SimulationTransition] = Field(default_factory=list)
    observations: list[SimulationObservation] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    provenance: ProvenanceLink | None = None


class DomainSimulationDescriptor(EM):
    domain: str
    arc: str
    status: BackendStatus
    classification: ResultClassification
    limitations: list[str] = Field(default_factory=list)


class PredictionHorizon(EM):
    steps: int = Field(ge=1)


class PredictionEvidence(EM):
    statement: str
    source: str | None = None
    status: EpistemicStatus = EpistemicStatus.OBSERVED


class PredictionConfidence(EM):
    value: float = Field(ge=0, le=1)
    basis: str
    measured_accuracy: str = "NOT_EVALUABLE"


class PredictionUncertainty(EM):
    statement: str
    status: EpistemicStatus = EpistemicStatus.UNKNOWN


class ForecastPoint(EM):
    step: int
    value: float
    status: EpistemicStatus


class PredictionRequest(EM):
    series: list[float]
    horizon: PredictionHorizon
    method: PredictionMethod
    rule_delta: float | None = None
    evidence: list[PredictionEvidence] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    provenance: ProvenanceLink | None = None


class PredictionOutput(EM):
    id: UUID = Field(default_factory=uuid4)
    points: list[ForecastPoint] = Field(default_factory=list)
    method: PredictionMethod
    horizon: int
    confidence: PredictionConfidence
    uncertainty: PredictionUncertainty
    assumptions: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    evidence: list[PredictionEvidence] = Field(default_factory=list)
    provenance: ProvenanceLink | None = None
    status: EpistemicStatus = EpistemicStatus.PREDICTED


class DifferenceItem(EM):
    variable: str
    baseline: float
    counterfactual: float
    delta: float


class CounterfactualResult(EM):
    id: UUID = Field(default_factory=uuid4)
    label: str = "COUNTERFACTUAL SIMULATION"
    causal_status: str = "CAUSAL HYPOTHESIS"
    verification: str = "NOT CAUSALLY VERIFIED"
    baseline: SimulationResult
    counterfactual: SimulationResult
    differences: list[DifferenceItem] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    uncertainty: str
    limitations: list[str] = Field(default_factory=list)
    provenance: ProvenanceLink | None = None


class PlanningAction(EM):
    name: str
    preconditions: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    deltas: list[StateVariable] = Field(default_factory=list)
    cost: float = 0
    risk: float = 0
    utility: float = 0
    estimated_outcome: str = ""


class PlanningProblem(EM):
    goal: EvolutionGoal
    initial_facts: list[str] = Field(default_factory=list)
    actions: list[PlanningAction] = Field(default_factory=list)
    constraints: list[EvolutionConstraint] = Field(default_factory=list)
    initial_state: SimulationState | None = None


class PlanStepRecord(EM):
    step_id: str
    description: str
    dependencies: list[str] = Field(default_factory=list)
    action: str | None = None


class PlanRecord(EM):
    id: UUID = Field(default_factory=uuid4)
    steps: list[PlanStepRecord] = Field(default_factory=list)
    core_plan_steps: list[str] = Field(default_factory=list)
    status: str = "PROPOSAL"
    feasible: bool = True
    failure: str | None = None


class PlanTerm(EM):
    name: str
    weight: float
    measured: float
    weighted: float


class PlanEvaluation(EM):
    plan_name: str
    feasible: bool
    terms: list[PlanTerm] = Field(default_factory=list)
    score: float
    basis: str
    constraint_violations: list[str] = Field(default_factory=list)
    predicted_outcome: float | None = None
    limitations: list[str] = Field(default_factory=list)


class PlanComparison(EM):
    evaluations: list[PlanEvaluation]
    selected_name: str | None = None
    basis: str
    hidden_criteria: bool = False
    approved: bool = False
    executed: bool = False


class CapabilityGap(EM):
    code: str
    statement: str
    source: str | None = None


class ProposedChange(EM):
    kind: str
    statement: str


class EvolutionProposal(EM):
    id: UUID = Field(default_factory=uuid4)
    gap: CapabilityGap
    target: str
    change: ProposedChange
    expected_benefit: str
    risks: list[str] = Field(default_factory=list)
    validation_requirement: str
    rollback_requirement: str
    human_approval: bool = False
    lifecycle: EvolutionLifecycle = EvolutionLifecycle.PROPOSAL
    states_visited: list[EvolutionLifecycle] = Field(default_factory=list)
    applied: bool = False
    version: str = "proposal-0"
    limitations: list[str] = Field(default_factory=list)
    provenance: ProvenanceLink | None = None


class QualityEvaluation(EM):
    subject: str
    status: str
    score: float | None = None
    basis: str
    limitations: list[str] = Field(default_factory=list)


class ReviewFinding(EM):
    category: str
    message: str
    severity: ReviewSeverity
