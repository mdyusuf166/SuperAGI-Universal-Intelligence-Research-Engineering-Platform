import asyncio
import importlib.util
from pathlib import Path

import pytest

from superagi.cognition import (
    ActionProposalService,
    ActionStatus,
    CognitiveContextBuilder,
    CognitiveCycle,
    CognitiveLifecycle,
    CognitivePipeline,
    CognitiveRouter,
    CognitiveStateMachine,
    CycleRequest,
    EpistemicStatus,
    LearningProposalService,
    NumericSignal,
    Observation,
    ObservationSource,
    OutcomeStatus,
    register_cognition_agents,
)
from superagi.cognition.perception import PerceptionLayer
from superagi.core.agents import AgentRegistry
from superagi.core.events import EventBus
from superagi.core.models import AgentContext, Task, TaskStatus
from superagi.memory import UniversalMemory
from superagi.orchestration import AgentCapabilityRegistry
from superagi.evolution.simulation import UnavailableSimulationBackend
from superagi.world_model import EntityType, EpistemicStatus as WorldEpistemic, KnowledgeGraph, WorldEntity, provenance_from

ROOT = Path(__file__).resolve().parents[1]


def load_demo(name):
    path = ROOT / "examples" / "cognition" / name
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request(**kwargs):
    payload = {"goal": "Draft a science hypothesis about moisture.", "approval_required": False, "source": "user-supplied note"}
    payload.update(kwargs)
    return CycleRequest(**payload)


def run_agent(agent, **values):
    task = Task(description=agent.metadata.name)
    return asyncio.run(agent.run(task, AgentContext(task_id=task.id, values=values)))


def test_lifecycle_rejects_invalid_transitions_and_cancel():
    machine = CognitiveStateMachine()
    with pytest.raises(ValueError, match="Invalid transition"):
        machine.move(CognitiveLifecycle.COMPLETED)
    machine.move(CognitiveLifecycle.INGESTING)
    machine.cancel()
    with pytest.raises(ValueError, match="Invalid transition"):
        machine.move(CognitiveLifecycle.REASONING)
    cycle = CognitiveCycle()
    cycle.cancel()
    cancelled = cycle.run(request())
    assert cancelled.lifecycle == CognitiveLifecycle.CANCELLED
    assert cancelled.executed is False
    assert cycle.tasks.get_task(cancelled.task_id).status == TaskStatus.CANCELLED


def test_ingestion_context_reasoning_and_unknowns():
    simulated = Observation(statement="Mock step.", source_kind=ObservationSource.SIMULATION, epistemic=EpistemicStatus.OBSERVED)
    ingested = PerceptionLayer().ingest([simulated], source=None)
    assert ingested.observations[0].epistemic == EpistemicStatus.SIMULATED
    unknown = Observation(statement="No source reading.", source_kind=ObservationSource.USER_INPUT, epistemic=EpistemicStatus.OBSERVED)
    assert PerceptionLayer().ingest([unknown], source=None).observations[0].epistemic == EpistemicStatus.UNKNOWN
    graph = KnowledgeGraph()
    for name in ("a", "b", "c", "d", "e"):
        graph.add_entity(WorldEntity(entity_type=EntityType.CONCEPT, name=name, epistemic=WorldEpistemic.UNKNOWN, provenance=provenance_from(None)))
    context = CognitiveContextBuilder().build(goal="world model query", observations=[], graph=graph, source=None)
    assert len(context.entities) == 4
    assert context.truncated is True
    state = CognitivePipeline().run(request(observations=[Observation(statement="Two notes disagree.", source_kind=ObservationSource.USER_INPUT, epistemic=EpistemicStatus.CONTRADICTED, evidence_refs=["note"])], source="user-supplied note"))
    assert "Two notes disagree." in state.reasoning_result.contradictions
    assert all(item.epistemic != EpistemicStatus.OBSERVED for item in state.reasoning_result.inferences)
    bare = CognitivePipeline().run(request(observations=[], source=None))
    assert "No evidenced claim was supplied for the goal." in bare.reasoning_result.unknowns
    assert bare.provenance.cycle.status == "MISSING"


def test_simulation_prediction_planning_decision_and_memory():
    memory = UniversalMemory()
    memory.remember("Moisture note supplied by the user.", source="user-supplied note")
    graph = KnowledgeGraph()
    graph.add_entity(WorldEntity(entity_type=EntityType.CONCEPT, name="moisture", epistemic=WorldEpistemic.EVIDENCED, provenance=provenance_from("user-supplied note")))
    bus = EventBus()
    state = CognitiveCycle(memory=memory, graph=graph, event_bus=bus).run(request(series=[1, 2, 3], simulate=True, predict=True, signals=[NumericSignal(name="moisture", value=3)], deltas=[NumericSignal(name="moisture", value=1)], assumptions=["The note was supplied by the user."]))
    assert state.lifecycle == CognitiveLifecycle.COMPLETED
    assert state.executed is False
    assert state.simulation_result.epistemic == EpistemicStatus.SIMULATED
    assert state.simulation_result.classification == "MOCK_SIMULATION"
    assert state.prediction_result.epistemic == EpistemicStatus.PREDICTED
    assert state.prediction_result.values == [4]
    assert state.prediction_result.measured_accuracy == "NOT_EVALUABLE"
    assert graph.annotations_for(graph.entities()[0].id)[0].property.epistemic == WorldEpistemic.PREDICTED
    assert graph.entities()[0].epistemic == WorldEpistemic.EVIDENCED
    assert state.plan_result.status == "PROPOSAL"
    assert state.plan_result.executed is False
    assert state.decision_result.criteria == ["risk"]
    assert state.decision_result.approved is False
    assert state.decision_result.executed is False
    assert state.memory_refs
    assert memory.search("Moisture")
    assert any(event.metadata.get("cognitive_event") == "CYCLE_STARTED" for event in bus.events())
    assert any(item.name == "goal_alignment" and item.status == "NOT_EVALUABLE" for item in state.evaluation.items)
    unavailable = CognitivePipeline().run(request(simulate=True, signals=[NumericSignal(name="moisture", value=1)]), simulation_backend=UnavailableSimulationBackend())
    assert unavailable.simulation_result.status == "SIMULATION_BACKEND_UNAVAILABLE"
    assert unavailable.plan_result.status == "PROPOSAL"
    assert "PLAN_CREATED" in [item.name.value for item in unavailable.events]
    assert unavailable.simulation_result.epistemic == EpistemicStatus.UNKNOWN


def test_approval_safety_learning_evolution_and_routing():
    waiting = CognitivePipeline().run(request(approval_required=True, human_approved=False, outcome=OutcomeStatus.OBSERVED_SUCCESS))
    assert waiting.lifecycle == CognitiveLifecycle.AWAITING_HUMAN_APPROVAL
    assert waiting.feedback.status == OutcomeStatus.NOT_EXECUTED
    assert waiting.action_proposals[0].approval_status == ActionStatus.PROPOSAL
    assert waiting.action_proposals[0].executed is False
    assert waiting.evolution_proposal.applied is False
    assert waiting.evolution_proposal.lifecycle == "AWAITING_HUMAN_APPROVAL"
    approved = CognitivePipeline().run(request(approval_required=True, human_approved=True))
    assert approved.lifecycle == CognitiveLifecycle.COMPLETED
    assert approved.action_proposals[0].approval_status == ActionStatus.APPROVED
    assert approved.action_proposals[0].executed is False
    assert approved.decision_result.approved is True
    with pytest.raises(PermissionError):
        ActionProposalService().execute(approved.action_proposals[0])
    with pytest.raises(PermissionError):
        LearningProposalService().apply(approved.learning_update)
    blocked = CognitivePipeline().run(request(goal="weapon deployment plan"))
    assert blocked.lifecycle == CognitiveLifecycle.FAILED
    assert blocked.executed is False
    assert "PLAN_CREATED" not in [item.name.value for item in blocked.events]
    route = CognitiveRouter().route("engineering design of a robot navigation aid")
    assert route.selected_winner is None
    assert route.conflict
    assert {item.domain for item in route.contributions} >= {"engineering", "robotics"}
    single = CognitiveRouter().route("Draft a science hypothesis")
    assert single.selected_winner == "research"


def test_agents_and_demos():
    from superagi.cognition.agents import AGENT_CLASSES, CognitiveCoordinatorAgent

    registry = AgentRegistry()
    capabilities = AgentCapabilityRegistry()
    register_cognition_agents(registry, capabilities)
    assert len(capabilities.discover(["cognition"], domain="cognition")) == len(AGENT_CLASSES) == 10
    result = run_agent(CognitiveCoordinatorAgent(), request=request())
    assert result.output["executed"] is False
    assert result.output["lifecycle"] == "COMPLETED"
    science = load_demo("scientific_cycle_demo.py").build()
    engineering = load_demo("engineering_cycle_demo.py").build()
    robot = load_demo("robot_cycle_demo.py").build()
    student = load_demo("student_cycle_demo.py").build()
    evolution = load_demo("evolution_proposal_demo.py").build()
    assert science["hypothesis"] is True
    assert science["prediction"] == "PREDICTED"
    assert science["executed"] is False
    assert engineering["plan_executed"] is False
    assert engineering["domain"] == "engineering"
    assert robot["robotics_backend"] == "UNAVAILABLE"
    assert robot["simulation"] == "SIMULATED"
    assert robot["executed"] is False
    assert student["integrity"] is True
    assert student["learning_applied"] is False
    assert evolution["lifecycle"] == "AWAITING_HUMAN_APPROVAL"
    assert evolution["simulation"] == "SIMULATION_BACKEND_UNAVAILABLE"
    assert evolution["evolution_applied"] is False
    assert evolution["apply_refused"] is True
