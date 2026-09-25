"""Adapters into ARC-02 memory and ARC-15 prediction, simulation, and planning."""

from __future__ import annotations

from superagi.evolution.models import (
    EvolutionConstraint,
    EvolutionGoal,
    PlanningAction,
    PlanningProblem,
    PredictionHorizon,
    PredictionMethod,
    PredictionRequest,
    SimulationAction,
    SimulationScenario,
    SimulationState,
    StateVariable,
    TerminationCondition,
)
from superagi.evolution.planning import ModelBasedPlanner, PlanningEngine
from superagi.evolution.prediction import PredictionEngine
from superagi.evolution.simulation import MockSimulationBackend, SimulationBackend
from superagi.memory.evidence.evidence import Evidence

from .graph import KnowledgeGraph
from .models import (
    DeclaredRecord,
    DomainDescriptor,
    DomainImportResult,
    EntityProperty,
    EntityStatus,
    EntityType,
    EpistemicStatus,
    EvidenceLinkStatus,
    LinkedResult,
    PropertyValue,
    TransitionKind,
    WorldEntity,
)
from .provenance import ProvenanceLog, provenance_from
from .updates import record_transition, snapshot_for
from .temporal import Timeline

_DOMAINS = (
    ("biomedical", "ARC-04", "No biomedical knowledge base is configured."),
    ("neuro", "ARC-05", "No neuro knowledge base is configured."),
    ("quantum", "ARC-06", "No quantum knowledge base is configured."),
    ("robotics", "ARC-07", "No robot world-model backend is configured."),
    ("cybersecurity", "ARC-08", "No cybersecurity knowledge base is configured."),
    ("education", "ARC-11", "No education knowledge base is configured."),
    ("science", "ARC-12", "No scientific knowledge base is configured."),
    ("engineering", "ARC-13", "No engineering knowledge base is configured."),
    ("personal", "ARC-10", "No personal knowledge base is configured."),
    ("collaboration", "ARC-14", "No collaboration knowledge base is configured."),
    ("environment", "ARC-16", "No environment knowledge base is configured."),
    ("space", "ARC-16", "No space knowledge base is configured."),
)


class MemoryAdapter:
    def entity_from_evidence(self, evidence: Evidence) -> WorldEntity:
        source = evidence.source.strip()
        epistemic = EpistemicStatus.EVIDENCED if source else EpistemicStatus.UNKNOWN
        return WorldEntity(
            entity_type=EntityType.CONCEPT,
            name=evidence.claim[:80],
            status=EntityStatus.PROPOSED,
            epistemic=epistemic,
            properties=[EntityProperty(name="claim", value=PropertyValue(text=evidence.claim), epistemic=epistemic, status=EvidenceLinkStatus.SUPPORTED if source else EvidenceLinkStatus.UNKNOWN, evidence_refs=[str(evidence.id)], provenance=provenance_from(source or None, evidence=[str(evidence.id)], agent="memory_adapter"))],
            provenance=provenance_from(source or None, evidence=[str(evidence.id)], agent="memory_adapter"),
        )

    def entity_from_memory(self, record) -> WorldEntity:
        source = (record.source or "").strip()
        epistemic = EpistemicStatus.EVIDENCED if source else EpistemicStatus.UNKNOWN
        return WorldEntity(
            entity_type=EntityType.CONCEPT,
            name=record.content[:80],
            status=EntityStatus.PROPOSED,
            epistemic=epistemic,
            properties=[EntityProperty(name="content", value=PropertyValue(text=record.content), epistemic=epistemic, evidence_refs=[str(record.id)], provenance=provenance_from(source or None, evidence=[str(record.id)], agent="memory_adapter"))],
            provenance=provenance_from(source or None, evidence=[str(record.id)], agent="memory_adapter"),
        )

    def remember(self, memory, summary: str, source: str | None) -> dict:
        link = ProvenanceLog().record(source=source, agent="memory_adapter", evidence=[summary], memory=memory if source else None)
        if link.status.value != "PRESENT":
            return {"stored": False, "provenance_status": "MISSING"}
        record = memory.remember(summary, source=source, tags=("world-model",))
        return {"stored": True, "provenance_status": "PRESENT", "id": str(record.id)}


class PredictionAdapter:
    def __init__(self, engine: PredictionEngine | None = None) -> None:
        self.engine = engine or PredictionEngine()

    def project(self, graph: KnowledgeGraph, timeline: Timeline, *, entity_id, property_name: str, series: list[float], method: PredictionMethod = PredictionMethod.PERSISTENCE, horizon: int = 1, source: str | None = None) -> LinkedResult:
        graph.get_entity(entity_id)
        output = self.engine.predict(PredictionRequest(series=series, horizon=PredictionHorizon(steps=horizon), method=method, assumptions=["Baseline forecast from caller-supplied series."]))
        if not output.points or output.status.value != "PREDICTED":
            return LinkedResult(stored=False, epistemic=EpistemicStatus.UNKNOWN, classification="NOT_EVALUABLE", limitations=output.limitations)
        point = output.points[0]
        prop = EntityProperty(name=property_name, value=PropertyValue(number=point.value), epistemic=EpistemicStatus.PREDICTED, confidence=output.confidence.value, status=EvidenceLinkStatus.UNKNOWN, provenance=provenance_from(source, agent="prediction_adapter"))
        graph.add_annotation(entity_id, prop)
        if series:
            observed = EpistemicStatus.OBSERVED if source else EpistemicStatus.UNKNOWN
            before = snapshot_for(entity_id, [EntityProperty(name=property_name, value=PropertyValue(number=series[-1]), epistemic=observed, provenance=provenance_from(source, agent="prediction_adapter"))], observed, max(len(series) - 1, 0), source)
            after = snapshot_for(entity_id, [prop], EpistemicStatus.PREDICTED, len(series), source)
            record_transition(timeline, previous=before, nxt=after, kind=TransitionKind.PREDICTED_TRANSITION, prediction_method=method.value, source=source)
        return LinkedResult(stored=True, epistemic=EpistemicStatus.PREDICTED, classification="PREDICTED", limitations=output.limitations + ["Stored as PREDICTED. Not an observed fact."])


class SimulationAdapter:
    def __init__(self, backend: SimulationBackend | None = None) -> None:
        self.backend = backend or MockSimulationBackend()

    def run(self, graph: KnowledgeGraph, timeline: Timeline, *, entity_id, variables: list[tuple[str, float]], deltas: list[tuple[str, float]], source: str | None = None) -> LinkedResult:
        graph.get_entity(entity_id)
        scenario = SimulationScenario(
            name="world-model",
            initial_state=SimulationState(variables=[StateVariable(name=name, value=value) for name, value in variables]),
            actions=[SimulationAction(name="step", deltas=[StateVariable(name=name, value=value) for name, value in deltas])],
            termination=TerminationCondition(max_steps=1),
        )
        result = self.backend.run(scenario)
        classification = result.classification.value
        if result.status.value != "COMPLETED":
            return LinkedResult(stored=False, epistemic=EpistemicStatus.UNKNOWN, classification=classification, limitations=result.limitations)
        last = result.trace[-1]
        props = [EntityProperty(name=item.name, value=PropertyValue(number=item.value), epistemic=EpistemicStatus.SIMULATED, provenance=provenance_from(source, agent="simulation_adapter")) for item in last.variables]
        for prop in props:
            graph.add_annotation(entity_id, prop)
        observed = EpistemicStatus.OBSERVED if source else EpistemicStatus.UNKNOWN
        before_props = [EntityProperty(name=name, value=PropertyValue(number=value), epistemic=observed, provenance=provenance_from(source, agent="simulation_adapter")) for name, value in variables]
        before = snapshot_for(entity_id, before_props, observed, 0, source)
        after = snapshot_for(entity_id, props, EpistemicStatus.SIMULATED, result.step_count, source)
        record_transition(timeline, previous=before, nxt=after, kind=TransitionKind.SIMULATED_TRANSITION, action_name="step", simulation_classification=classification, source=source)
        return LinkedResult(stored=True, epistemic=EpistemicStatus.SIMULATED, classification=classification, limitations=result.limitations + ["Stored as SIMULATED. Not an observed fact."])


class PlanningAdapter:
    def evaluate(self, *, goal_statement: str, actions: list[PlanningAction], constraints: list[EvolutionConstraint] | None = None, variables: list[tuple[str, float]] | None = None, weights: dict[str, float] | None = None, outcome_variable: str = "value"):
        initial = SimulationState(variables=[StateVariable(name=name, value=value) for name, value in variables]) if variables else None
        problem = PlanningProblem(goal=EvolutionGoal(statement=goal_statement), actions=list(actions), constraints=list(constraints or []), initial_state=initial)
        comparison = ModelBasedPlanner().compare(problem, {"primary": list(actions)}, weights or {"cost": 1.0}, outcome_variable)
        plan = PlanningEngine().plan(problem)
        return {"comparison": comparison, "plan": plan, "executed": False, "status": "PROPOSAL"}


class WorldModelDomainAdapter:
    def __init__(self, descriptor: DomainDescriptor) -> None:
        self.descriptor = descriptor

    def import_backend(self) -> DomainImportResult:
        return DomainImportResult(domain=self.descriptor.domain, status=self.descriptor.status, entities=[], limitations=list(self.descriptor.limitations))

    def map_declared(self, records: list[DeclaredRecord]) -> list[WorldEntity]:
        mapped = []
        for record in records:
            source = (record.source or "").strip()
            epistemic = record.epistemic
            if epistemic == EpistemicStatus.OBSERVED and not source:
                epistemic = EpistemicStatus.UNKNOWN
            mapped.append(
                WorldEntity(
                    entity_type=record.entity_type,
                    name=record.name,
                    status=EntityStatus.PROPOSED if epistemic != EpistemicStatus.OBSERVED else EntityStatus.OBSERVED,
                    epistemic=epistemic,
                    properties=[EntityProperty(name="statement", value=PropertyValue(text=record.statement or record.name), epistemic=epistemic, provenance=provenance_from(source or None, agent="domain_adapter"))] if record.statement or record.name else [],
                    provenance=provenance_from(source or None, agent="domain_adapter"),
                )
            )
        return mapped


class WorldModelDomainRegistry:
    def __init__(self) -> None:
        self._items = {domain: DomainDescriptor(domain=domain, arc=arc, status="UNAVAILABLE", limitations=[reason]) for domain, arc, reason in _DOMAINS}

    def get(self, domain: str) -> DomainDescriptor:
        try:
            return self._items[domain]
        except KeyError as exc:
            raise KeyError(f"Unknown world-model domain: {domain}") from exc

    def adapter(self, domain: str) -> WorldModelDomainAdapter:
        return WorldModelDomainAdapter(self.get(domain))

    def domains(self) -> list[str]:
        return sorted(self._items)
