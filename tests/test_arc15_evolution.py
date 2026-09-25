import asyncio
import importlib.util
from pathlib import Path

import pytest

from superagi.collaboration import register_collaboration_agents
from superagi.core.agents import AgentRegistry
from superagi.core.models import AgentContext, Task
from superagi.evolution import (
    BackendStatus,
    CapabilityGap,
    CounterfactualEngine,
    DomainSimulationRegistry,
    EvolutionConstraint,
    EvolutionCycle,
    EvolutionGoal,
    EvolutionLifecycle,
    EvolutionPipeline,
    EvolutionSafetyPolicy,
    register_evolution_agents,
    MetaEvaluator,
    MockSimulationBackend,
    ModelBasedPlanner,
    PlanningAction,
    PlanningEngine,
    PlanningProblem,
    PredictionEngine,
    PredictionHorizon,
    PredictionMethod,
    PredictionRequest,
    ResultClassification,
    SimulationAction,
    SimulationScenario,
    SimulationState,
    StateVariable,
    TerminationCondition,
    UnavailableSimulationBackend,
    WorldEntity,
    WorldModel,
)
from superagi.evolution.agents import (
    CounterfactualAgent,
    EvolutionAgent,
    EvolutionReviewAgent,
    PlanningAgent,
    PredictionAgent,
    SimulationAgent,
    WorldModelAgent,
)
from superagi.memory import UniversalMemory
from superagi.orchestration import AgentCapabilityRegistry, UniversalIntelligenceCoordinator, IntelligenceRequest

ROOT = Path(__file__).resolve().parents[1]


def load_demo(name):
    path = ROOT / "examples" / "evolution" / name
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def state(*pairs):
    return SimulationState(variables=[StateVariable(name=name, value=value) for name, value in pairs])


def run_agent(agent, **values):
    task = Task(description=agent.metadata.name)
    return asyncio.run(agent.run(task, AgentContext(task_id=task.id, values=values)))


def test_simulation_transitions_failure_and_unavailable_backend():
    scenario = SimulationScenario(name="margin", initial_state=state(("power", 5), ("margin", 1)), actions=[SimulationAction(name="reduce", deltas=[StateVariable(name="power", value=-1)])], termination=TerminationCondition(max_steps=1))
    result = MockSimulationBackend().run(scenario)
    assert result.status == BackendStatus.COMPLETED
    assert result.classification == ResultClassification.MOCK_SIMULATION
    assert result.step_count == 1
    assert [item.value("power") for item in result.trace] == [5, 4]
    assert result.transitions[0].action == "reduce"
    bad = SimulationScenario(name="bad", initial_state=state(("power", 1)), actions=[SimulationAction(name="missing", deltas=[StateVariable(name="voltage", value=1)])])
    failed = MockSimulationBackend().run(bad)
    assert failed.status == BackendStatus.FAILED
    unavailable = UnavailableSimulationBackend().run(scenario)
    assert unavailable.status == BackendStatus.UNAVAILABLE
    assert unavailable.classification == ResultClassification.BACKEND_UNAVAILABLE
    assert unavailable.trace == []


def test_domain_descriptors_stay_unavailable_except_the_mock():
    registry = DomainSimulationRegistry()
    for domain in ("biology", "chemistry", "neuro", "quantum", "robotics", "cybersecurity", "education", "science", "engineering", "collaboration"):
        assert registry.get(domain).status == BackendStatus.UNAVAILABLE
    assert registry.get("deterministic-mock").status == BackendStatus.MOCK
    assert registry.adapter("quantum").simulate(SimulationScenario(name="q", initial_state=state(("q", 0)))).classification == ResultClassification.BACKEND_UNAVAILABLE


def test_prediction_baselines_uncertainty_and_ground_truth():
    engine = PredictionEngine()
    persistence = engine.predict(PredictionRequest(series=[1, 2, 3], horizon=PredictionHorizon(steps=2), method=PredictionMethod.PERSISTENCE))
    average = engine.predict(PredictionRequest(series=[1, 2, 3], horizon=PredictionHorizon(steps=2), method=PredictionMethod.MOVING_AVERAGE))
    trend = engine.predict(PredictionRequest(series=[1, 2, 3], horizon=PredictionHorizon(steps=2), method=PredictionMethod.LINEAR_TREND))
    rule = engine.predict(PredictionRequest(series=[3], horizon=PredictionHorizon(steps=2), method=PredictionMethod.RULE_BASED, rule_delta=2))
    unknown = engine.predict(PredictionRequest(series=[3], horizon=PredictionHorizon(steps=1), method=PredictionMethod.LINEAR_TREND))
    assert [point.value for point in persistence.points] == [3, 3]
    assert [point.value for point in average.points] == [2, 2]
    assert [point.value for point in trend.points] == [4, 5]
    assert [point.value for point in rule.points] == [5, 7]
    assert persistence.points[0].status.value == "PREDICTED"
    assert persistence.confidence.measured_accuracy == "NOT_EVALUABLE"
    assert unknown.status.value == "UNKNOWN"
    scored = MetaEvaluator().prediction(persistence, [3, 3])
    assert scored.status == "COMPUTED"
    assert scored.score == 0
    assert MetaEvaluator().prediction(persistence).status == "NOT_EVALUABLE"


def test_counterfactual_is_not_causal_verification():
    initial = state(("level", 1))
    baseline = SimulationScenario(name="base", initial_state=initial, actions=[SimulationAction(name="add", deltas=[StateVariable(name="level", value=1)])], termination=TerminationCondition(max_steps=1))
    alternative = SimulationScenario(name="alt", initial_state=initial, actions=[SimulationAction(name="add-more", deltas=[StateVariable(name="level", value=3)])], termination=TerminationCondition(max_steps=1))
    result = CounterfactualEngine(MockSimulationBackend()).compare(baseline, alternative)
    assert result.label == "COUNTERFACTUAL SIMULATION"
    assert result.causal_status == "CAUSAL HYPOTHESIS"
    assert result.verification == "NOT CAUSALLY VERIFIED"
    assert result.differences[0].delta == 2


def test_planning_orders_dependencies_and_reports_constraint_violations():
    first = PlanningAction(name="collect", postconditions=["collected"])
    second = PlanningAction(name="review", dependencies=["collect"], preconditions=["collected"], postconditions=["reviewed"], cost=5)
    problem = PlanningProblem(goal=EvolutionGoal(statement="reviewed"), initial_facts=[], actions=[second, first], constraints=[EvolutionConstraint(kind="max_cost", limit=1)])
    plan = PlanningEngine().plan(problem)
    assert [step.step_id for step in plan.steps] == ["collect", "review"]
    assert plan.core_plan_steps[0].startswith("Analyze:")
    assert plan.feasible is False
    assert "max_cost" in plan.failure
    blocked = PlanningEngine().plan(PlanningProblem(goal=EvolutionGoal(statement="done"), actions=[PlanningAction(name="go", preconditions=["ready"])]))
    assert blocked.status == "FAILED"
    comparison = ModelBasedPlanner().compare(PlanningProblem(goal=EvolutionGoal(statement="choose"), initial_state=state(("power", 2))), {"costly": [PlanningAction(name="costly", cost=5, deltas=[StateVariable(name="power", value=1)])], "cheap": [PlanningAction(name="cheap", cost=1, deltas=[StateVariable(name="power", value=1)])]}, {"cost": 1}, "power")
    assert comparison.selected_name == "cheap"
    assert comparison.hidden_criteria is False
    assert comparison.executed is False
    assert comparison.basis.startswith("Lowest explicit weighted sum")


def test_world_model_and_provenance_use_existing_memory():
    model = WorldModel()
    model.add_entity(WorldEntity(name="monitor", properties=[StateVariable(name="power", value=1)]))
    assert model.remember(UniversalMemory(), None)["stored"] is False
    assert model.provenance.missing is True
    memory = UniversalMemory()
    stored = model.remember(memory, "user note")
    assert stored["stored"] is True
    assert memory.search("monitor")
    assert memory.provenance.records


def test_evolution_proposal_stops_before_apply_and_rejects_unsafe_requests():
    proposal = EvolutionCycle().propose(CapabilityGap(code="prediction_uncertainty", statement="Forecast error was not measured."), source="evaluation")
    assert proposal.lifecycle == EvolutionLifecycle.AWAITING_HUMAN_APPROVAL
    assert proposal.applied is False
    assert "APPLY" not in EvolutionLifecycle.__members__
    approved = EvolutionCycle().propose(CapabilityGap(code="tool_gap", statement="A described tool is missing."), approved=True, source="user")
    assert approved.lifecycle == EvolutionLifecycle.PROPOSAL
    assert approved.human_approval is True
    assert approved.applied is False
    with pytest.raises(PermissionError):
        EvolutionCycle().apply(approved)
    with pytest.raises(PermissionError):
        EvolutionCycle().propose(CapabilityGap(code="modify source code", statement="modify source code automatically"))
    assert EvolutionSafetyPolicy().assess("simulation")["allowed"] is True
    assert EvolutionSafetyPolicy().assess("weapon deployment")["allowed"] is False


def test_pipeline_human_gate_and_agents_register():
    result = EvolutionPipeline().run(goal="Draft a mock plan.", initial_state=state(("power", 1)), actions=[SimulationAction(name="hold", deltas=[StateVariable(name="power", value=0)])], series=[1], candidates={"primary": [PlanningAction(name="hold", cost=1, deltas=[StateVariable(name="power", value=0)])]}, weights={"cost": 1}, outcome_variable="power", source="declared", approval=True)
    assert result["executed"] is False
    assert result["decision_approved"] is True
    assert result["classification"] == "SIMULATION_ONLY"
    rejected = EvolutionPipeline().run(goal="modify source code now", initial_state=state(("power", 1)), actions=[], series=[1], candidates={}, weights={}, outcome_variable="power")
    assert rejected["status"] == "FAILED"
    registry = AgentCapabilityRegistry()
    register_evolution_agents(AgentRegistry(), registry)
    register_collaboration_agents(AgentRegistry(), registry)
    assert len(registry.discover(["evolution"], domain="evolution")) == 7
    assert registry.discover(["planning"], domain="evolution")[0].name == "evolution_planning_agent"
    assert registry.discover(["planning"], domain="planning")[0].name == "planning_agent"
    report = UniversalIntelligenceCoordinator(registry, memory=UniversalMemory()).solve(IntelligenceRequest(goal="Draft a mock plan.", capabilities=["evolution"], execution_mode="COMPUTATIONAL"))
    assert report.limitations
    scenario = SimulationScenario(name="s", initial_state=state(("power", 1)), actions=[SimulationAction(name="hold", deltas=[StateVariable(name="power", value=0)])], termination=TerminationCondition(max_steps=1))
    assert run_agent(SimulationAgent(), scenario=scenario).output["classification"] == "MOCK_SIMULATION"
    request = PredictionRequest(series=[1, 1], horizon=PredictionHorizon(steps=1), method=PredictionMethod.PERSISTENCE)
    assert run_agent(PredictionAgent(), request=request).output["measured_accuracy"] == "NOT_EVALUABLE"
    problem = PlanningProblem(goal=EvolutionGoal(statement="hold"), actions=[PlanningAction(name="hold")])
    assert run_agent(PlanningAgent(), problem=problem).output["executed"] is False
    other = SimulationScenario(name="o", initial_state=state(("power", 1)), actions=[SimulationAction(name="up", deltas=[StateVariable(name="power", value=1)])], termination=TerminationCondition(max_steps=1))
    assert run_agent(CounterfactualAgent(), baseline=scenario, alternative=other).output["verification"] == "NOT CAUSALLY VERIFIED"
    assert run_agent(WorldModelAgent()).output["stored"] is False
    gap = CapabilityGap(code="evidence_gap", statement="No source was supplied.")
    evolved = run_agent(EvolutionAgent(), gap=gap, source="user")
    assert evolved.output["applied"] is False
    review = run_agent(EvolutionReviewAgent(), proposal=EvolutionCycle().propose(gap, source=None))
    assert review.success is False


def test_demos_are_deterministic_and_do_not_execute():
    engineering = load_demo("engineering_simulation_demo.py").build()
    robot = load_demo("robot_navigation_demo.py").build()
    science = load_demo("scientific_prediction_demo.py").build()
    proposal = load_demo("evolution_proposal_demo.py").build()
    assert engineering["banner"][0] == "SIMULATION ONLY"
    assert engineering["domain_status"] == "UNAVAILABLE"
    assert engineering["power"] == [5, 4]
    assert engineering["executed"] is False
    assert robot["trace"] == robot["path"]
    assert robot["robotics_backend"] == "UNAVAILABLE"
    assert robot["executed"] is False
    assert science["prediction"] == [4, 5]
    assert science["prediction_accuracy"] == "NOT_EVALUABLE"
    assert "NON-EXECUTING" in science["experiment"]
    assert science["executed"] is False
    assert proposal["lifecycle"] == "AWAITING_HUMAN_APPROVAL"
    assert proposal["applied"] is False
    assert proposal["apply_refused"] is True
    assert load_demo("robot_navigation_demo.py").build()["path"] == robot["path"]
