import asyncio
import importlib.util
from pathlib import Path

import pytest

from superagi.collaboration import (
    MAX_CONTEXT_ITEMS,
    STAGE_ORDER,
    Claim,
    CollaborationPipeline,
    Consent,
    ConsentState,
    ContextItem,
    ContextService,
    CoordinationService,
    DecisionSupport,
    GoalService,
    InteractionMode,
    Person,
    Preference,
    RecommendationEngine,
    RoleAssigner,
    SafetyPolicy,
    SessionStore,
    TaskCoordinator,
    register_collaboration_agents,
)
from superagi.collaboration.agents import (
    CollaborationAgent,
    CommunicationAgent,
    CoordinationAgent,
    DecisionSupportAgent,
    PlanningAgent,
    ReviewAgent,
)
from superagi.core.agents import AgentRegistry
from superagi.core.models import AgentContext, Task
from superagi.education import AcademicIntegrityPolicy, LearningPathPlanner
from superagi.engineering import register_engineering_agents
from superagi.memory import UniversalMemory
from superagi.orchestration import AgentCapabilityRegistry
from superagi.personal.services import GoalManager, PersonalMemoryService
from superagi.science.integration import science_agent_descriptor

ROOT = Path(__file__).resolve().parents[1]


def load_demo(filename):
    path = ROOT / "examples" / "collaboration" / filename
    spec = importlib.util.spec_from_file_location(filename[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_agent(agent, **values):
    task = Task(description=agent.metadata.name)
    return asyncio.run(agent.run(task, AgentContext(task_id=task.id, values=values)))


def consent(persistent=False):
    return Consent(state=ConsentState.GRANTED, scope=["persistent"] if persistent else ["session"], persistent=persistent)


def pipeline(**overrides):
    values = {
        "participants": ["ada"],
        "roles": [RoleAssigner().assign("ada", "decision maker", human=True)],
        "consent": consent(),
        "goal_statements": ["Draft a plan"],
        "task_specs": [{"title": "Review the draft", "owner": "ada", "evidence": ["user note"], "completion_criteria": ["Human review"]}],
        "evidence": ("user note",),
        "sources": ("user note",),
    }
    values.update(overrides)
    return CollaborationPipeline().run("Draft a collaborative plan", **values)


def test_models_do_not_carry_inferred_sensitive_fields():
    person = Person(display_name="ada")
    assert person.display_name == "ada"
    assert set(Person.model_fields) == {"id", "display_name", "consent"}
    with pytest.raises(PermissionError):
        SafetyPolicy().check_preference(Preference(key="health", value="unknown"))


def test_consent_blocks_persistent_storage_and_allows_session_context():
    memory = UniversalMemory()
    service = ContextService(memory, PersonalMemoryService(memory))
    item = ContextItem(text="Ada prefers morning reviews", source="user")
    denied = service.store([item], Consent(state=ConsentState.DENIED, persistent=True, scope=["persistent"]))
    absent = service.store([item], Consent())
    assert denied["persisted"] is False
    assert absent["mode"] == "session-only"
    assert service.recall("morning") == []
    granted = service.store([item], consent(persistent=True))
    assert granted["persisted"] is True
    assert service.recall("morning", limit=5)


def test_context_is_bounded():
    items = [ContextItem(text=f"item {index}", source="user") for index in range(MAX_CONTEXT_ITEMS + 1)]
    built = ContextService().build(items, consent())
    assert len(built["items"]) == MAX_CONTEXT_ITEMS
    assert built["truncated"] is True
    store = SessionStore("bounded")
    for index in range(12):
        store.add_participant(f"p{index}")
    with pytest.raises(ValueError):
        store.add_participant("overflow")


def test_goals_remain_user_controlled_and_publish_through_arc10():
    service = GoalService()
    goal = service.create("Learn the method", priority=2, milestones=("read",))
    children = service.decompose(goal, ["Read the notes"])
    assert goal.statement == "Learn the method"
    assert children[0].proposed is True
    assert children[0].parent_id == goal.id
    with pytest.raises(PermissionError):
        service.rename(goal, "A different goal", user_authorized=False)
    service.add_evidence(goal, "Finished the first note")
    assert goal.progress_evidence == ["Finished the first note"]
    with pytest.raises(PermissionError):
        service.publish(goal, GoalManager(), persistent_consent=False)
    published = service.publish(goal, GoalManager(), persistent_consent=True)
    assert goal.personal_goal_id == published.id


def test_tasks_link_to_core_tasks_and_surface_cycles():
    coordinator = TaskCoordinator()
    first = coordinator.create("collect", "ada")
    second = coordinator.create("review", "ada", dependencies=(first.id,))
    assert first.core_task_id is not None
    assert [task.title for task in coordinator.order()["ordered"]] == ["collect", "review"]
    second.dependencies = [first.id]
    first.dependencies = [second.id]
    cycled = coordinator.order()
    assert cycled["cycle"] is True
    failed = pipeline(task_specs=[
        {"title": "collect", "owner": "ada", "depends_on": ["review"], "evidence": ["user note"], "completion_criteria": ["done"]},
        {"title": "review", "owner": "ada", "depends_on": ["collect"], "evidence": ["user note"], "completion_criteria": ["done"]},
    ])
    assert failed["status"] == "FAILED"
    assert failed["stage"] == "dependencies"
    assert failed["executed"] is False


def test_recommendations_stay_separate_from_decisions_and_actions():
    recommendation = RecommendationEngine().recommend([
        {"name": "defer", "criteria": {"risk": 2}, "evidence": ["note"], "assumptions": ["no deadline"]},
        {"name": "review", "criteria": {"risk": 1}, "evidence": ["note"], "assumptions": ["human is available"]},
    ])
    assert recommendation.text == "review"
    assert recommendation.status.value == "RECOMMENDATION"
    assert recommendation.alternatives == ["defer"]
    prepared = DecisionSupport().prepare(question="Which next step?", options=[{"name": "review", "criteria": {"risk": 1}, "evidence": ["note"], "assumptions": []}], criteria=["risk"], evidence=["note"], assumptions=[], risks=["none supplied"], tradeoffs="Lower risk sum.")
    assert prepared["decision"].approved is False
    assert prepared["decision"].status == "PROPOSAL"
    assert prepared["executed"] is False
    action = RecommendationEngine().draft_action(recommendation)
    assert action.status.value == "DRAFT"
    assert action.executed is False


@pytest.mark.parametrize("text", ["autonomous irreversible action", "unauthorized external post", "hidden personal collection", "infer health condition", "political preference", "api key", "dangerous physical operation", "autonomous deployment", "cheat on the active exam"])
def test_safety_rejects_disallowed_requests(text):
    assert SafetyPolicy().assess(text)["allowed"] is False


@pytest.mark.parametrize("text", ["planning", "drafting", "summarization", "simulation", "decision support", "research assistance", "project coordination"])
def test_safety_allows_assistance(text):
    assert SafetyPolicy().assess(text)["allowed"] is True


def test_pipeline_reports_without_executing_and_waits_for_approval():
    completed = pipeline()
    assert completed["status"] == "COMPLETED"
    assert completed["stages"] == list(STAGE_ORDER)
    assert completed["executed"] is False
    assert completed["decision"].status == "PROPOSAL"
    assert completed["action"].executed is False
    assert completed["core_plan"][0].startswith("Analyze:")
    waiting = pipeline(mode=InteractionMode.HUMAN_APPROVAL_REQUIRED, approval=False)
    assert waiting["status"] == "AWAITING_HUMAN_APPROVAL"
    assert waiting["executed"] is False
    approved = pipeline(mode=InteractionMode.HUMAN_APPROVAL_REQUIRED, approval=True)
    assert approved["status"] == "COMPLETED"
    assert approved["decision"].approved is True
    assert approved["action"].status.value == "APPROVED_ACTION"
    assert approved["action"].executed is False


def test_coordination_keeps_conflicts_visible():
    registry = AgentCapabilityRegistry()
    register_collaboration_agents(AgentRegistry(), registry)
    result = CoordinationService().coordinate("Draft a plan", registry, ["collaboration"])
    assert result["selected_conflict_winner"] is None
    assert result["executed_external"] is False
    assert result["orchestration_conflicts"]
    conflicts = CoordinationService().claim_conflicts([
        Claim(topic="scope", claim="narrow", source="ada"),
        Claim(topic="scope", claim="broad", source="research agent"),
    ])
    assert conflicts[0].resolved is False
    assert conflicts[0].claims == ["narrow", "broad"]


def test_agents_cover_planning_communication_and_review():
    planned = run_agent(PlanningAgent(), goal="Draft a plan", constraints=["time"], milestones=["outline"], verification_criteria=["Human review"])
    assert planned.output["steps"][0].startswith("Analyze:")
    assert planned.output["executed"] is False
    summary = run_agent(CommunicationAgent())
    assert summary.output["meeting_summary"] == "meetings: not provided"
    assert "invented participant" not in summary.output["participants"]
    assert summary.output["fabricated"] is False
    supplied = run_agent(CommunicationAgent(), meetings=["Notes supplied by Ada"], participants=["Ada"], sources=["Ada"])
    assert "Notes supplied by Ada" in supplied.output["meeting_summary"]
    assert supplied.output["sources"] == ["Ada"]
    empty = run_agent(ReviewAgent(), objective="")
    assert empty.success is False
    support = run_agent(DecisionSupportAgent(), question="Which next step?", options=[{"name": "review", "criteria": {"risk": 1}}], criteria=["risk"], evidence=["note"], assumptions=[], risks=[], tradeoffs="Lower risk.")
    assert support.output["status"] == "PROPOSAL"
    assert support.output["executed"] is False
    registry = AgentCapabilityRegistry()
    register_collaboration_agents(AgentRegistry(), registry)
    coordinated = run_agent(CoordinationAgent(), objective="Draft a plan", registry=registry, capabilities=["planning"], claims=[{"topic": "scope", "claim": "narrow", "source": "ada"}, {"topic": "scope", "claim": "broad", "source": "bee"}])
    assert coordinated.output["selected_conflict_winner"] is None
    assert len(coordinated.output["claim_conflicts"][0]["claims"]) == 2
    assisted = run_agent(CollaborationAgent(), objective="Draft a collaborative plan", consent=consent(), participants=["ada"], sources=["user note"], evidence=["user note"])
    assert assisted.output["executed"] is False


def test_public_and_arc_integrations():
    import superagi.collaboration as collaboration
    import superagi.collaboration.agents as agents
    assert collaboration.CollaborationPipeline is CollaborationPipeline
    assert agents.ReviewAgent is ReviewAgent
    registry = AgentCapabilityRegistry()
    core = AgentRegistry()
    register_collaboration_agents(core, registry)
    register_engineering_agents(AgentRegistry(), registry)
    registry.register(science_agent_descriptor())
    assert len(registry.discover(["planning"], domain="planning")) == 1
    assert registry.discover(["coordination"], domain="coordination")
    assert registry.discover(["decision_support"], domain="decision_support")
    assert registry.discover(["personal"])
    assert registry.discover(["engineering"], domain="engineering")
    assert registry.discover(["science"], domain="science")
    assert AcademicIntegrityPolicy().assess("submit for me")["allowed"] is False
    assert SafetyPolicy().assess("write my exam")["allowed"] is False
    assert AcademicIntegrityPolicy().assess("Plan a study sequence")["allowed"] is True
    assert LearningPathPlanner is not None


def test_demos_are_deterministic_and_do_not_execute():
    research = load_demo("research_team_collaboration.py").build()
    assert research["status"] == "COMPLETED"
    assert research["executed"] is False
    assert research["hypothesis_status"] == "PROPOSED"
    assert "NON-EXECUTING" in research["experiment"]
    assert research["knowledge"]["HYPOTHESIS"]
    assert research["knowledge"]["FACT"] == []
    assert research["winner"] is None
    assert research["roles"] == ["decision maker", "research", "evidence", "critic"]
    student = load_demo("student_research_planning.py").build()
    assert student["integrity_allowed"] is True
    assert student["status"] == "AWAITING_HUMAN_APPROVAL"
    assert student["executed"] is False
    assert student["learning_tasks"] == ["evidence review", "experiment design"]
    assert student["gaps"] == ["experiment design"]
    assert student["approval"]["executed"] is False
    engineering = load_demo("engineering_team_design_review.py").build()
    assert engineering["engineering_status"] == "COMPLETED"
    assert engineering["executed"] is False
    assert engineering["engineering_executed"] is False
    assert "SIMULATION-ONLY" in engineering["classification"][1]
    assert engineering["winner"] is None
    assert load_demo("research_team_collaboration.py").build()["hypothesis"] == research["hypothesis"]
