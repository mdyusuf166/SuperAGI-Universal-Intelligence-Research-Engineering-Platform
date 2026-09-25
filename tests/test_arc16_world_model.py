import asyncio
import importlib.util
from pathlib import Path

import pytest
from pydantic import ValidationError

from superagi.core.agents import AgentRegistry
from superagi.core.models import AgentContext, Task
from superagi.evolution.models import PlanningAction
from superagi.evolution.registration import register_evolution_agents
from superagi.evolution.simulation import UnavailableSimulationBackend
from superagi.memory import UniversalMemory
from superagi.memory.evidence.evidence import Evidence
from superagi.orchestration import AgentCapabilityRegistry
from superagi.world_model import (
    BoundedReasoner,
    DeclaredRecord,
    EntityProperty,
    EntityStatus,
    EntityType,
    EpistemicStatus,
    KnowledgeGraph,
    MemoryAdapter,
    PipelineRequest,
    PlanningAdapter,
    PredictionAdapter,
    PropertyValue,
    ProvenanceStatus,
    RelationType,
    ResolutionStatus,
    SimulationAdapter,
    TemporalOrder,
    TimeInterval,
    TimePoint,
    Timeline,
    TransitionKind,
    WorldConstraint,
    WorldEntity,
    WorldEvent,
    WorldGoal,
    WorldModelDomainRegistry,
    WorldModelPipeline,
    WorldModelSafetyPolicy,
    WorldRelation,
    WorldQuery,
    WorldTransition,
    combine,
    provenance_from,
    record_transition,
    register_world_model_agents,
    snapshot_for,
)
from superagi.world_model.agents import ConflictDetectionAgent, KnowledgeGraphAgent, WorldModelAgent, WorldQueryAgent, WorldStateAgent

ROOT = Path(__file__).resolve().parents[1]


def load_demo(name):
    path = ROOT / "examples" / "world_model" / name
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entity(name, kind=EntityType.CONCEPT, epistemic=EpistemicStatus.UNKNOWN, status=EntityStatus.UNKNOWN, source=None, properties=None):
    return WorldEntity(entity_type=kind, name=name, status=status, epistemic=epistemic, properties=list(properties or []), provenance=provenance_from(source, agent="test"))


def run_agent(agent, **values):
    task = Task(description=agent.metadata.name)
    return asyncio.run(agent.run(task, AgentContext(task_id=task.id, values=values)))


def test_models_reject_untyped_payloads_and_bad_enums():
    with pytest.raises(ValidationError):
        PropertyValue()
    with pytest.raises(ValidationError):
        PropertyValue(number=1, text="1")
    with pytest.raises(ValidationError):
        WorldRelation(source_id=entity("a").id, relation="NOT_A_RELATION", target_id=entity("b").id)
    observed = entity("pump", epistemic=EpistemicStatus.OBSERVED, status=EntityStatus.OBSERVED, source=None)
    assert observed.provenance.status == ProvenanceStatus.MISSING


def test_graph_paths_duplicates_and_prohibited_self_links():
    graph = KnowledgeGraph()
    alpha = graph.add_entity(entity("alpha"))
    beta = graph.add_entity(entity("beta"))
    gamma = graph.add_entity(entity("gamma"))
    delta = graph.add_entity(entity("delta"))
    with pytest.raises(ValueError, match="Duplicate entity"):
        graph.add_entity(entity("alpha"))
    graph.add_relation(WorldRelation(source_id=alpha.id, relation=RelationType.CONNECTED_TO, target_id=beta.id, epistemic=EpistemicStatus.EVIDENCED))
    graph.add_relation(WorldRelation(source_id=alpha.id, relation=RelationType.CONNECTED_TO, target_id=gamma.id, epistemic=EpistemicStatus.EVIDENCED))
    graph.add_relation(WorldRelation(source_id=beta.id, relation=RelationType.CONNECTED_TO, target_id=delta.id))
    graph.add_relation(WorldRelation(source_id=gamma.id, relation=RelationType.CONNECTED_TO, target_id=delta.id))
    with pytest.raises(ValueError, match="Duplicate relation"):
        graph.add_relation(WorldRelation(source_id=alpha.id, relation=RelationType.CONNECTED_TO, target_id=beta.id))
    with pytest.raises(ValueError, match="Self-referential"):
        graph.add_relation(WorldRelation(source_id=alpha.id, relation=RelationType.PART_OF, target_id=alpha.id))
    graph.add_relation(WorldRelation(source_id=alpha.id, relation=RelationType.RELATED_TO, target_id=alpha.id, epistemic=EpistemicStatus.UNKNOWN))
    with pytest.raises(ValueError, match="Invalid entity reference"):
        graph.add_relation(WorldRelation(source_id=alpha.id, relation=RelationType.USES, target_id=entity("missing").id))
    assert [item.name for item in graph.neighbors(alpha.id)] == ["beta", "gamma"]
    assert [graph.get_entity(item).name for item in graph.path(alpha.id, delta.id)] == ["alpha", "beta", "delta"]
    child = graph.subgraph([alpha.id, beta.id])
    assert [item.name for item in child.entities()] == ["alpha", "beta"]
    assert len(child.get_relations(relation=RelationType.CONNECTED_TO)) == 1
    assert any(item.relation == RelationType.RELATED_TO for item in child.get_relations())
    beta_edge = next(item for item in graph.get_relations(entity_id=beta.id, relation=RelationType.CONNECTED_TO) if item.source_id == beta.id)
    removed = graph.remove_relation(beta_edge.id)
    assert removed.target_id == delta.id
    assert [graph.get_entity(item).name for item in graph.path(alpha.id, delta.id)] == ["alpha", "gamma", "delta"]
    assert graph.validate() == []


def test_causal_hypothesis_is_not_verified_and_inference_is_labeled():
    graph = KnowledgeGraph()
    marker = graph.add_entity(entity("marker"))
    cell = graph.add_entity(entity("cell"))
    culture = graph.add_entity(entity("culture"))
    idea = graph.add_entity(entity("idea", kind=EntityType.HYPOTHESIS, epistemic=EpistemicStatus.HYPOTHESIZED, status=EntityStatus.PROPOSED))
    trial = graph.add_entity(entity("trial", kind=EntityType.EXPERIMENT, epistemic=EpistemicStatus.UNKNOWN, status=EntityStatus.PROPOSED))
    graph.add_relation(WorldRelation(source_id=marker.id, relation=RelationType.PART_OF, target_id=cell.id, epistemic=EpistemicStatus.EVIDENCED, provenance=provenance_from("note")))
    graph.add_relation(WorldRelation(source_id=cell.id, relation=RelationType.PART_OF, target_id=culture.id, epistemic=EpistemicStatus.EVIDENCED, provenance=provenance_from("note")))
    causal = graph.add_relation(WorldRelation(source_id=idea.id, relation=RelationType.CAUSES_HYPOTHESIS, target_id=trial.id, epistemic=EpistemicStatus.OBSERVED, status="SUPPORTED"))
    correlated = graph.add_relation(WorldRelation(source_id=marker.id, relation=RelationType.CORRELATED_WITH, target_id=trial.id, epistemic=EpistemicStatus.EVIDENCED))
    inferred = BoundedReasoner().infer_transitive(graph, RelationType.PART_OF)
    assert causal.epistemic == EpistemicStatus.HYPOTHESIZED
    assert causal.verification == "NOT CAUSALLY VERIFIED"
    assert causal.status.value == "UNKNOWN"
    assert correlated.verification == "NOT CAUSATION"
    assert inferred[0].epistemic == EpistemicStatus.INFERRED
    assert inferred[0].provenance.status == ProvenanceStatus.MISSING
    with pytest.raises(ValueError, match="not configured"):
        BoundedReasoner().infer_transitive(graph, RelationType.RELATED_TO)


def test_temporal_transitions_keep_simulated_and_predicted_labels():
    timeline = Timeline()
    assert timeline.order(0, 1) == TemporalOrder.BEFORE
    assert timeline.order(2, 1) == TemporalOrder.AFTER
    assert timeline.intervals(TimeInterval(start=0, end=5), TimeInterval(start=1, end=2)) == TemporalOrder.DURING
    assert timeline.intervals(TimeInterval(start=0, end=3), TimeInterval(start=2, end=5)) == TemporalOrder.OVERLAP
    holder = entity("holder")
    graph = KnowledgeGraph()
    graph.add_entity(holder)
    graph.add_event(WorldEvent(name="reading", entity_ids=[holder.id], time=TimePoint(step=1, label="t1"), epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("bench")))
    observed = snapshot_for(holder.id, [], EpistemicStatus.OBSERVED, 0, "bench")
    later = snapshot_for(holder.id, [], EpistemicStatus.OBSERVED, 1, "bench")
    simulated = snapshot_for(holder.id, [], EpistemicStatus.SIMULATED, 2, "bench")
    record_transition(timeline, previous=observed, nxt=later, kind=TransitionKind.OBSERVED_TRANSITION, source="bench")
    record_transition(timeline, previous=later, nxt=simulated, kind=TransitionKind.SIMULATED_TRANSITION, simulation_classification="MOCK_SIMULATION", source="bench")
    assert timeline.state_at(1).epistemic == EpistemicStatus.OBSERVED
    assert timeline.state_at(2).epistemic == EpistemicStatus.SIMULATED
    with pytest.raises(ValueError, match="SIMULATED_TRANSITION"):
        timeline.add_transition(WorldTransition(kind=TransitionKind.OBSERVED_TRANSITION, previous_id=later.id, next_id=simulated.id))


def test_prediction_simulation_and_planning_do_not_overwrite_observations():
    graph = KnowledgeGraph()
    pump = graph.add_entity(entity("pump", kind=EntityType.COMPONENT, epistemic=EpistemicStatus.OBSERVED, status=EntityStatus.OBSERVED, source="schematic", properties=[EntityProperty(name="power", value=PropertyValue(number=5), epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("schematic"))]))
    timeline = Timeline()
    predicted = PredictionAdapter().project(graph, timeline, entity_id=pump.id, property_name="power", series=[1, 2, 3], method=__import__("superagi.evolution.models", fromlist=["PredictionMethod"]).PredictionMethod.LINEAR_TREND, source="series")
    assert predicted.epistemic == EpistemicStatus.PREDICTED
    assert predicted.stored is True
    assert graph.get_entity(pump.id).properties[0].value.number == 5
    assert graph.get_entity(pump.id).properties[0].epistemic == EpistemicStatus.OBSERVED
    assert graph.annotations_for(pump.id, EpistemicStatus.PREDICTED)[0].property.value.number == 4
    simulated = SimulationAdapter().run(graph, timeline, entity_id=pump.id, variables=[("power", 5)], deltas=[("power", -1)], source="schematic")
    assert simulated.classification == "MOCK_SIMULATION"
    assert graph.annotations_for(pump.id, EpistemicStatus.SIMULATED)[0].property.value.number == 4
    assert graph.get_entity(pump.id).properties[0].epistemic == EpistemicStatus.OBSERVED
    unavailable = SimulationAdapter(UnavailableSimulationBackend()).run(graph, Timeline(), entity_id=pump.id, variables=[("power", 5)], deltas=[("power", -1)], source="schematic")
    assert unavailable.stored is False
    assert unavailable.classification == "BACKEND_UNAVAILABLE"
    planned = PlanningAdapter().evaluate(goal_statement="Review the pump.", actions=[PlanningAction(name="review", cost=1, risk=0)], variables=[("power", 5)], weights={"cost": 1}, outcome_variable="power")
    assert planned["executed"] is False
    assert planned["plan"].status == "PROPOSAL"
    assert planned["comparison"].executed is False
    assert planned["comparison"].hidden_criteria is False


def test_memory_provenance_contradictions_and_queries():
    evidence = Evidence(claim="The pump is listed on the schematic.", source="schematic", source_type="user")
    mapped = MemoryAdapter().entity_from_evidence(evidence)
    assert mapped.epistemic == EpistemicStatus.EVIDENCED
    assert mapped.provenance.status == ProvenanceStatus.PRESENT
    orphan = MemoryAdapter().entity_from_evidence(Evidence(claim="Orphan claim with no source.", source="", source_type="user"))
    assert orphan.epistemic == EpistemicStatus.UNKNOWN
    assert orphan.provenance.status == ProvenanceStatus.MISSING
    memory = UniversalMemory()
    stored = MemoryAdapter().remember(memory, "World model entities: pump.", "schematic")
    assert stored["stored"] is True
    assert memory.search("pump")
    assert MemoryAdapter().remember(memory, "orphan", None)["provenance_status"] == "MISSING"
    graph = KnowledgeGraph()
    sensor = graph.add_entity(entity("sensor", kind=EntityType.DEVICE, epistemic=EpistemicStatus.EVIDENCED, source="bench", properties=[EntityProperty(name="temperature", value=PropertyValue(number=20), epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["note-20"], provenance=provenance_from("note-20"))]))
    other = graph.add_entity(entity("other"))
    graph.add_relation(WorldRelation(source_id=sensor.id, relation=RelationType.SUPPORTS, target_id=other.id, status="SUPPORTED", epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["note-20"], provenance=provenance_from("note-20")))
    graph.add_relation(WorldRelation(source_id=sensor.id, relation=RelationType.CONTRADICTS, target_id=other.id, epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["note-40"], provenance=provenance_from("note-40")))
    graph.update_entity(sensor.id, properties=[EntityProperty(name="temperature", value=PropertyValue(number=40), epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["note-40"], provenance=provenance_from("note-40"))])
    conflicts = graph.detect_contradictions()
    subjects = {item.subject for item in conflicts}
    assert "temperature" in subjects
    assert "SUPPORTS/CONTRADICTS" in subjects
    temperature = next(item for item in conflicts if item.subject == "temperature")
    assert temperature.resolution_status == ResolutionStatus.UNRESOLVED
    assert sorted(item.number for item in temperature.conflicting_values) == [20, 40]
    assert graph.resolve_conflict(temperature.id, evidence_ref="missing", rule="no").resolution_status == ResolutionStatus.UNRESOLVED
    resolved = graph.resolve_conflict(temperature.id, evidence_ref="note-20", rule="caller selected note-20")
    assert resolved.resolution_status == ResolutionStatus.RESOLVED
    assert {prop.epistemic for prop in graph.get_entity(sensor.id).properties if prop.name == "temperature"} == {EpistemicStatus.CONTRADICTED}
    query = WorldQuery(graph)
    assert query.find_by_property("temperature", PropertyValue(number=20)) == []
    assert query.find_supporting_evidence(graph.get_relations(relation=RelationType.SUPPORTS)[0].id) == ["note-20"]
    assert query.find_contradictions()
    assert any(item.status == ProvenanceStatus.PRESENT for item in query.find_provenance_chain(sensor.id))
    assert combine([0.2, 0.4]).measured_accuracy == "NOT_EVALUABLE"
    unknown = graph.add_entity(entity("gap"))
    assert query.find_entity("gap")[0].epistemic == EpistemicStatus.UNKNOWN
    assert unknown.status == EntityStatus.UNKNOWN


def test_domains_agents_safety_and_pipeline():
    registry = WorldModelDomainRegistry()
    for domain in ("biomedical", "neuro", "quantum", "robotics", "cybersecurity", "education", "science", "engineering", "personal", "collaboration", "environment", "space"):
        result = registry.adapter(domain).import_backend()
        assert result.status == "UNAVAILABLE"
        assert result.entities == []
    mapped = registry.adapter("science").map_declared([DeclaredRecord(name="culture", entity_type=EntityType.CELL, epistemic=EpistemicStatus.OBSERVED)])
    assert mapped[0].epistemic == EpistemicStatus.UNKNOWN
    assert WorldModelSafetyPolicy().assess("research modeling of a pump")["allowed"] is True
    assert WorldModelSafetyPolicy().assess("weapon control")["allowed"] is False
    with pytest.raises(PermissionError):
        KnowledgeGraph().add_entity(entity("store credential for the bench"))
    pump = entity("pump", kind=EntityType.COMPONENT, epistemic=EpistemicStatus.OBSERVED, status=EntityStatus.OBSERVED, source="schematic")
    part = entity("valve", kind=EntityType.COMPONENT)
    request = PipelineRequest(entities=[pump, part], relations=[WorldRelation(source_id=part.id, relation=RelationType.PART_OF, target_id=pump.id, epistemic=EpistemicStatus.EVIDENCED, provenance=provenance_from("schematic"))], goal=WorldGoal(statement="Review the pump."), series=[1, 2, 3], predict_property="power", simulate_variables=[("power", 5)], simulate_deltas=[("power", -1)], transitive="PART_OF", source="schematic")
    report, graph, _timeline = WorldModelPipeline().run(request, memory=UniversalMemory())
    assert report.status == "COMPLETED"
    assert report.executed is False
    assert report.plan_executed is False
    assert report.predicted is True
    assert report.simulated is True
    assert report.plan_status == "PROPOSAL"
    assert EpistemicStatus.PREDICTED.value in report.epistemic_labels
    assert EpistemicStatus.SIMULATED.value in report.epistemic_labels
    blocked, _, _ = WorldModelPipeline().run(PipelineRequest(entities=[entity("weapon control sketch")]))
    assert blocked.status == "FAILED"
    assert blocked.executed is False
    agents = AgentRegistry()
    capabilities = AgentCapabilityRegistry()
    register_world_model_agents(agents, capabilities)
    register_evolution_agents(AgentRegistry(), capabilities)
    assert len(capabilities.discover(["world_model"], domain="world_model")) == 5
    assert capabilities.discover(["world_model"], domain="evolution")[0].name == "world_model_agent"
    assert run_agent(WorldModelAgent(), entities=[entity("solo")]).output["executed"] is False
    graph = KnowledgeGraph()
    left = graph.add_entity(entity("left"))
    right = graph.add_entity(entity("right"))
    assert run_agent(KnowledgeGraphAgent(), graph=graph, relations=[WorldRelation(source_id=left.id, relation=RelationType.RELATED_TO, target_id=right.id)]).output["executed"] is False
    assert run_agent(WorldQueryAgent(), graph=graph, name="left").output["epistemic"] == ["UNKNOWN"]
    assert run_agent(ConflictDetectionAgent(), graph=graph).output["resolution"] == []
    timeline = Timeline()
    timeline.add_snapshot(snapshot_for(left.id, [], EpistemicStatus.SIMULATED, 1, None))
    assert run_agent(WorldStateAgent(), timeline=timeline).output["snapshots"][0][0] == "SIMULATED"
    assert graph.validate() == []


def test_demos_keep_epistemic_labels():
    science = load_demo("scientific_knowledge_graph_demo.py").build()
    engineering = load_demo("engineering_world_model_demo.py").build()
    robot = load_demo("robot_world_state_demo.py").build()
    conflict = load_demo("contradiction_demo.py").build()
    assert science["causal_verification"] == "NOT CAUSALLY VERIFIED"
    assert science["inferred"] == "INFERRED"
    assert science["experiment"] == "UNKNOWN"
    assert science["executed"] is False
    assert engineering["plan_executed"] is False
    assert engineering["plan_status"] == "PROPOSAL"
    assert engineering["inferred"] == "INFERRED"
    assert engineering["sensor"] == "UNKNOWN"
    assert robot["observed_x"] == 0
    assert robot["simulated_x"] == 1
    assert robot["simulated_epistemic"] == "SIMULATED"
    assert robot["robotics_backend"] == "UNAVAILABLE"
    assert robot["classification"] == "MOCK_SIMULATION"
    assert robot["executed"] is False
    assert conflict["values"] == [20, 40]
    assert conflict["resolution"] == "UNRESOLVED"
    assert conflict["epistemic"] == ["CONTRADICTED"]
    assert conflict["selected"] is None
