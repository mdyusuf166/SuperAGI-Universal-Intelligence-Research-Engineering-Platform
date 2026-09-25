"""Typed records for the universal world model. Dictionaries are not the representation."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WM(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EpistemicStatus(str, Enum):
    OBSERVED = "OBSERVED"
    EVIDENCED = "EVIDENCED"
    INFERRED = "INFERRED"
    HYPOTHESIZED = "HYPOTHESIZED"
    PREDICTED = "PREDICTED"
    SIMULATED = "SIMULATED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"


class EntityStatus(str, Enum):
    KNOWN = "KNOWN"
    OBSERVED = "OBSERVED"
    PROPOSED = "PROPOSED"
    UNKNOWN = "UNKNOWN"


class EntityType(str, Enum):
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    AGENT = "AGENT"
    ROBOT = "ROBOT"
    DEVICE = "DEVICE"
    MOLECULE = "MOLECULE"
    GENE = "GENE"
    CELL = "CELL"
    DISEASE = "DISEASE"
    MATERIAL = "MATERIAL"
    COMPONENT = "COMPONENT"
    SYSTEM = "SYSTEM"
    SOFTWARE = "SOFTWARE"
    DATASET = "DATASET"
    PAPER = "PAPER"
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT = "EXPERIMENT"
    LOCATION = "LOCATION"
    ENVIRONMENT = "ENVIRONMENT"
    PLAN = "PLAN"
    TASK = "TASK"
    PROJECT = "PROJECT"
    EVENT = "EVENT"
    CONCEPT = "CONCEPT"


class RelationType(str, Enum):
    PART_OF = "PART_OF"
    CONTAINS = "CONTAINS"
    CONNECTED_TO = "CONNECTED_TO"
    DEPENDS_ON = "DEPENDS_ON"
    CAUSES_HYPOTHESIS = "CAUSES_HYPOTHESIS"
    CORRELATED_WITH = "CORRELATED_WITH"
    PRECEDES = "PRECEDES"
    FOLLOWS = "FOLLOWS"
    LOCATED_IN = "LOCATED_IN"
    USES = "USES"
    PRODUCES = "PRODUCES"
    REQUIRES = "REQUIRES"
    CONTRADICTS = "CONTRADICTS"
    SUPPORTS = "SUPPORTS"
    DERIVED_FROM = "DERIVED_FROM"
    RELATED_TO = "RELATED_TO"


class EvidenceLinkStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTESTED = "CONTESTED"
    UNKNOWN = "UNKNOWN"
    CONTRADICTED = "CONTRADICTED"


class ProvenanceStatus(str, Enum):
    PRESENT = "PRESENT"
    MISSING = "MISSING"


class TransitionKind(str, Enum):
    OBSERVED_TRANSITION = "OBSERVED_TRANSITION"
    SIMULATED_TRANSITION = "SIMULATED_TRANSITION"
    PREDICTED_TRANSITION = "PREDICTED_TRANSITION"


class ResolutionStatus(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    RESOLVED = "RESOLVED"


class TemporalOrder(str, Enum):
    BEFORE = "BEFORE"
    AFTER = "AFTER"
    DURING = "DURING"
    OVERLAP = "OVERLAP"


class PropertyValue(WM):
    number: float | None = None
    text: str | None = None

    @model_validator(mode="after")
    def one_payload(self) -> "PropertyValue":
        if (self.number is None) == (self.text is None):
            raise ValueError("PropertyValue requires exactly one of number or text")
        return self

    def key(self) -> str:
        if self.number is not None:
            return f"n:{self.number}"
        return f"t:{self.text}"


class ProvenanceRef(WM):
    id: UUID = Field(default_factory=uuid4)
    source: str | None = None
    agent: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    status: ProvenanceStatus = ProvenanceStatus.MISSING
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def status_matches_source(self) -> "ProvenanceRef":
        if self.source:
            self.status = ProvenanceStatus.PRESENT
        else:
            self.source = None
            self.status = ProvenanceStatus.MISSING
        return self


class EntityProperty(WM):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    value: PropertyValue
    unit: str = ""
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: EvidenceLinkStatus = EvidenceLinkStatus.UNKNOWN
    evidence_refs: list[str] = Field(default_factory=list)
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class WorldEntity(WM):
    id: UUID = Field(default_factory=uuid4)
    entity_type: EntityType
    name: str = Field(min_length=1)
    status: EntityStatus = EntityStatus.UNKNOWN
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    confidence: float | None = Field(default=None, ge=0, le=1)
    properties: list[EntityProperty] = Field(default_factory=list)
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class WorldRelation(WM):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    relation: RelationType
    target_id: UUID
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: EvidenceLinkStatus = EvidenceLinkStatus.UNKNOWN
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    causal_status: str = ""
    verification: str = ""
    basis: str = ""
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class TimePoint(WM):
    step: int = Field(ge=0)
    label: str = ""


class TimeInterval(WM):
    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @model_validator(mode="after")
    def ordered(self) -> "TimeInterval":
        if self.end < self.start:
            raise ValueError("Time interval end is before start")
        return self


class TemporalLink(WM):
    id: UUID = Field(default_factory=uuid4)
    earlier_step: int
    later_step: int
    order: TemporalOrder
    created_at: datetime = Field(default_factory=utc_now)


class WorldEvent(WM):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    entity_ids: list[UUID] = Field(default_factory=list)
    time: TimePoint
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class WorldObservation(WM):
    id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    property_name: str
    value: PropertyValue
    epistemic: EpistemicStatus = EpistemicStatus.OBSERVED
    evidence_refs: list[str] = Field(default_factory=list)
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class WorldAction(WM):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    actor_id: UUID | None = None
    target_ids: list[UUID] = Field(default_factory=list)
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class WorldConstraint(WM):
    id: UUID = Field(default_factory=uuid4)
    statement: str
    kind: str
    limit: float | None = None
    entity_id: UUID | None = None
    property_name: str | None = None
    status: str = "PROPOSED"
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class WorldGoal(WM):
    id: UUID = Field(default_factory=uuid4)
    statement: str = Field(min_length=1)
    status: str = "PROPOSED"
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class EntityState(WM):
    id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    properties: list[EntityProperty] = Field(default_factory=list)
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    time: TimePoint
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)


class WorldState(WM):
    id: UUID = Field(default_factory=uuid4)
    label: str
    entity_states: list[EntityState] = Field(default_factory=list)
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class WorldSnapshot(WM):
    id: UUID = Field(default_factory=uuid4)
    time: TimePoint
    state: WorldState
    epistemic: EpistemicStatus
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class WorldTransition(WM):
    id: UUID = Field(default_factory=uuid4)
    kind: TransitionKind
    previous_id: UUID
    next_id: UUID
    event_id: UUID | None = None
    action_name: str = ""
    observations: list[WorldObservation] = Field(default_factory=list)
    prediction_method: str | None = None
    simulation_classification: str | None = None
    provenance: ProvenanceRef = Field(default_factory=ProvenanceRef)
    created_at: datetime = Field(default_factory=utc_now)


class Conflict(WM):
    id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    subject: str
    conflicting_values: list[PropertyValue] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    resolution_status: ResolutionStatus = ResolutionStatus.UNRESOLVED
    resolution_rule: str | None = None
    selected_evidence: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ValidationIssue(WM):
    code: str
    message: str


class Annotation(WM):
    id: UUID = Field(default_factory=uuid4)
    entity_id: UUID
    property: EntityProperty
    created_at: datetime = Field(default_factory=utc_now)


class StateDelta(WM):
    name: str
    before: PropertyValue | None = None
    after: PropertyValue | None = None
    before_epistemic: EpistemicStatus
    after_epistemic: EpistemicStatus


class ConstraintCheck(WM):
    constraint_id: UUID
    satisfied: bool
    detail: str


class EvidenceAggregate(WM):
    status: EvidenceLinkStatus
    confidence: float | None = None
    basis: str
    count: int


class UncertaintyReport(WM):
    confidence: float | None
    basis: str
    measured_accuracy: str = "NOT_EVALUABLE"


class QueryHit(WM):
    kind: str
    label: str
    epistemic: EpistemicStatus
    ref_id: str


class DomainDescriptor(WM):
    domain: str
    arc: str
    status: str
    limitations: list[str] = Field(default_factory=list)


class DeclaredRecord(WM):
    name: str
    entity_type: EntityType
    source: str | None = None
    epistemic: EpistemicStatus = EpistemicStatus.UNKNOWN
    statement: str = ""


class DomainImportResult(WM):
    domain: str
    status: str
    entities: list[WorldEntity] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class LinkedResult(WM):
    stored: bool
    epistemic: EpistemicStatus
    classification: str
    limitations: list[str] = Field(default_factory=list)
