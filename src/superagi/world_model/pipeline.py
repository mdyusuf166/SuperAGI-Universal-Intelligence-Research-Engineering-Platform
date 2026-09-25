"""Deterministic world-model pipeline. It does not call a model or the network."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .adapters import MemoryAdapter, PlanningAdapter, PredictionAdapter, SimulationAdapter
from .graph import KnowledgeGraph
from .models import EpistemicStatus, WorldConstraint, WorldEntity, WorldEvent, WorldGoal, WorldRelation
from .query import WorldQuery
from .reasoning import BoundedReasoner
from .temporal import Timeline
from .validation import WorldModelSafetyPolicy


class PipelineRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entities: list[WorldEntity]
    relations: list[WorldRelation] = Field(default_factory=list)
    events: list[WorldEvent] = Field(default_factory=list)
    goal: WorldGoal | None = None
    constraints: list[WorldConstraint] = Field(default_factory=list)
    series: list[float] = Field(default_factory=list)
    predict_property: str | None = None
    simulate_variables: list[tuple[str, float]] = Field(default_factory=list)
    simulate_deltas: list[tuple[str, float]] = Field(default_factory=list)
    transitive: str | None = None
    source: str | None = None


class WorldModelReport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str
    executed: bool = False
    stages: list[str] = Field(default_factory=list)
    entity_names: list[str] = Field(default_factory=list)
    epistemic_labels: list[str] = Field(default_factory=list)
    conflict_subjects: list[str] = Field(default_factory=list)
    inferred_count: int = 0
    predicted: bool = False
    simulated: bool = False
    plan_status: str | None = None
    plan_executed: bool = False
    provenance_missing: int = 0
    safety_allowed: bool = True
    limitations: list[str] = Field(default_factory=list)


class WorldModelPipeline:
    def __init__(self) -> None:
        self.safety = WorldModelSafetyPolicy()
        self.memory = MemoryAdapter()
        self.prediction = PredictionAdapter()
        self.simulation = SimulationAdapter()
        self.planning = PlanningAdapter()
        self.reasoner = BoundedReasoner()

    def run(self, request: PipelineRequest, *, memory=None) -> tuple[WorldModelReport, KnowledgeGraph, Timeline]:
        text = " ".join([entity.name for entity in request.entities] + [request.goal.statement if request.goal else ""])
        safety = self.safety.assess(text)
        stages = ["INPUT", "ENTITY REGISTRATION", "RELATION REGISTRATION", "STATE CONSTRUCTION", "TEMPORAL UPDATE", "EVIDENCE LINKING", "CONTRADICTION CHECK", "QUERY / REASONING", "PROVENANCE", "WORLD MODEL REPORT"]
        if not safety["allowed"]:
            report = WorldModelReport(status="FAILED", executed=False, stages=stages, safety_allowed=False, limitations=["Safety policy rejected the request."])
            return report, KnowledgeGraph(), Timeline()
        graph = KnowledgeGraph()
        timeline = Timeline()
        for entity in request.entities:
            graph.add_entity(entity)
        for relation in request.relations:
            graph.add_relation(relation)
        for event in request.events:
            graph.add_event(event)
        inferred = []
        if request.transitive:
            from .models import RelationType

            inferred = self.reasoner.infer_transitive(graph, RelationType(request.transitive))
        predicted = False
        simulated = False
        if request.series and request.predict_property and graph.entities():
            linked = self.prediction.project(graph, timeline, entity_id=graph.entities()[0].id, property_name=request.predict_property, series=request.series, source=request.source)
            predicted = linked.stored
        if request.simulate_variables and graph.entities():
            linked = self.simulation.run(graph, timeline, entity_id=graph.entities()[0].id, variables=request.simulate_variables, deltas=request.simulate_deltas or [("value", 0.0)], source=request.source)
            simulated = linked.stored
        plan_status = None
        if request.goal is not None:
            from superagi.evolution.models import PlanningAction

            actions = [PlanningAction(name="review-context", cost=1, risk=0, estimated_outcome="Review the recorded world model.")]
            planned = self.planning.evaluate(goal_statement=request.goal.statement, actions=actions, variables=request.simulate_variables or None, outcome_variable=request.simulate_variables[0][0] if request.simulate_variables else "value")
            plan_status = planned["status"]
        conflicts = graph.detect_contradictions()
        query = WorldQuery(graph, timeline)
        labels = sorted({entity.epistemic.value for entity in graph.entities()} | {relation.epistemic.value for relation in graph.get_relations()})
        if predicted:
            labels.append(EpistemicStatus.PREDICTED.value)
        if simulated:
            labels.append(EpistemicStatus.SIMULATED.value)
        missing = sum(1 for entity in graph.entities() if entity.provenance.status.value == "MISSING")
        if request.source and memory is not None:
            self.memory.remember(memory, "World model entities: " + ", ".join(entity.name for entity in graph.entities()), request.source)
        elif request.source is None:
            missing = max(missing, 1)
        report = WorldModelReport(
            status="COMPLETED",
            executed=False,
            stages=stages,
            entity_names=[entity.name for entity in graph.entities()],
            epistemic_labels=sorted(set(labels)),
            conflict_subjects=[item.subject for item in conflicts],
            inferred_count=len(inferred),
            predicted=predicted,
            simulated=simulated,
            plan_status=plan_status,
            plan_executed=False,
            provenance_missing=missing,
            safety_allowed=True,
            limitations=[
                "Relations are not truth guarantees.",
                "INFERRED, PREDICTED, and SIMULATED labels were not promoted to OBSERVED.",
            ],
        )
        return report, graph, timeline
