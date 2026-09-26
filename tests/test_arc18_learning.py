import asyncio
import importlib.util
from pathlib import Path

import pytest

from superagi.cognition import CognitivePipeline, CycleRequest
from superagi.collaboration.models import Consent, ConsentState, Preference
from superagi.core.agents import AgentRegistry
from superagi.core.models import AgentContext, Task
from superagi.education.models import Curriculum, StudentProfile, Topic
from superagi.evolution.simulation import UnavailableSimulationBackend
from superagi.learning import (
    ADAPTATION_TARGETS,
    AdaptationProposal,
    AdaptationService,
    AssessmentStatus,
    CognitiveLearningAdapter,
    CrossDomainSkillReuse,
    EducationLearningAdapter,
    ExperienceAnalyzer,
    ExperienceKind,
    ExperienceRecord,
    GapType,
    KnowledgeGap,
    KnowledgeGapDetector,
    LearningAssessment,
    LearningEpisode,
    LearningEvidence,
    LearningExperience,
    LearningLifecycle,
    LearningMemoryAdapter,
    LearningObjective,
    LearningOutcome,
    LearningPipeline,
    LearningPlan,
    LearningPlanner,
    LearningProposal,
    LearningRequest,
    LearningSafetyPolicy,
    LearningStateMachine,
    LearningStep,
    LearningTask,
    LearningUpdate,
    LessonKind,
    PersonalLearningAdapter,
    PracticeEngine,
    PracticeMode,
    PracticeTask,
    Skill,
    SkillAssessment,
    SkillClaim,
    SkillGraph,
    SkillPrerequisite,
    SkillStatus,
    SkillTransferProposal,
    SkillType,
    SkillValidator,
    TransferService,
    ValidationCriteria,
    WorldModelLearningAdapter,
    learning_descriptors,
    provenance,
    register_learning_agents,
)
from superagi.memory import UniversalMemory
from superagi.orchestration import AgentCapabilityRegistry
from superagi.personal.services import GoalManager, LearningManager, ProjectManager
from superagi.world_model import EpistemicStatus as WorldEpistemic, KnowledgeGraph

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ["Python", "ML", "Deep Learning", "Computer Vision", "Biomedical Vision"]


def load_demo(name):
    path = ROOT / "examples" / "learning" / name
    spec = importlib.util.spec_from_file_location(name[:-3], path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_agent(agent, **values):
    task = Task(description=agent.metadata.name)
    return asyncio.run(agent.run(task, AgentContext(task_id=task.id, values=values)))


def chain_graph(declared=("Python",)):
    graph = SkillGraph()
    for name in CHAIN:
        graph.add_skill(Skill(name=name, skill_type=SkillType.PROGRAMMING, status=SkillStatus.DECLARED if name in declared else SkillStatus.PROPOSED))
    for later, earlier in zip(CHAIN[1:], CHAIN):
        graph.add_prerequisite(SkillPrerequisite(skill=later, required=earlier))
    return graph


def double(value):
    return value * 2


def passing_code(skill, times=2):
    engine = PracticeEngine()
    return [engine.code(skill, double, [((1,), 2), ((3,), 6)], source="tests") for _ in range(times)]


def test_models_are_typed_and_default_to_proposals():
    for cls in (LearningTask, LearningObjective, LearningEpisode, LearningEvidence, LearningOutcome, KnowledgeGap, LearningProposal, LearningPlan, LearningStep, LearningAssessment, LearningUpdate, AdaptationProposal):
        assert "id" in cls.model_fields
        assert cls.model_config.get("extra") == "forbid"
    assert LearningExperience is ExperienceRecord
    assert "provenance" in ExperienceRecord.model_fields
    assert set(SkillType.__members__) >= {"KNOWLEDGE", "PROGRAMMING", "ROBOTICS", "QUANTUM", "EDUCATION", "COLLABORATION"}
    assert set(SkillStatus.__members__) == {"DECLARED", "PROPOSED", "PRACTICED", "EVALUATED", "VALIDATED", "UNKNOWN"}
    assert "limitations" in Skill.model_fields
    assert "real-world competence" in Skill(name="x", skill_type=SkillType.KNOWLEDGE).limitations[0]
    with pytest.raises(ValueError):
        LearningTask(goal="x", unexpected=True)
    with pytest.raises(ValueError):
        ValidationCriteria(min_passing_episodes=1)
    assert LearningPlan(goal="x").status == "PROPOSAL"
    assert LearningUpdate(skill="x", proposed_status=SkillStatus.VALIDATED).applied is False


def test_lifecycle_transitions_fail_explicitly():
    machine = LearningStateMachine()
    for step in (LearningLifecycle.PROPOSED, LearningLifecycle.PLANNED, LearningLifecycle.PRACTICING, LearningLifecycle.ASSESSING, LearningLifecycle.VALIDATING, LearningLifecycle.READY_FOR_UPDATE, LearningLifecycle.AWAITING_HUMAN_APPROVAL, LearningLifecycle.UPDATED):
        machine.move(step)
    assert machine.history[-1] == LearningLifecycle.UPDATED
    with pytest.raises(ValueError):
        machine.move(LearningLifecycle.PROPOSED)
    skipping = LearningStateMachine()
    with pytest.raises(ValueError):
        skipping.move(LearningLifecycle.UPDATED)
    with pytest.raises(ValueError):
        LearningStateMachine().move(LearningLifecycle.READY_FOR_UPDATE)


def test_skill_graph_chain_queries():
    graph = chain_graph()
    assert graph.order() == CHAIN
    assert graph.dependencies("Biomedical Vision") == CHAIN[:-1]
    assert graph.prerequisites("Deep Learning") == ["ML"]
    assert graph.dependents("ML") == ["Biomedical Vision", "Computer Vision", "Deep Learning"]
    assert graph.ready_skills({"Python"}) == ["ML"]
    assert graph.ready_skills() == ["Python"]
    assert graph.validate() == []
    assert graph.get_skill("biomedical vision").status == SkillStatus.PROPOSED


def test_skill_graph_rejects_cycles_duplicates_and_bad_references():
    graph = chain_graph()
    with pytest.raises(ValueError):
        graph.add_prerequisite(SkillPrerequisite(skill="Python", required="Biomedical Vision"))
    assert graph.validate() == []
    with pytest.raises(ValueError):
        graph.add_skill(Skill(name="python", skill_type=SkillType.PROGRAMMING))
    with pytest.raises(ValueError):
        graph.add_prerequisite(SkillPrerequisite(skill="ML", required="Missing"))
    with pytest.raises(ValueError):
        graph.add_prerequisite(SkillPrerequisite(skill="ML", required="ML"))
    with pytest.raises(KeyError):
        graph.get_skill("Missing")
    graph.get_skill("ML").status = SkillStatus.VALIDATED
    assert "validated without evidence: ML" in graph.validate()


def test_gap_detection_requires_evidence_or_requirements():
    detector = KnowledgeGapDetector()
    assert detector.detect() == []
    graph = chain_graph()
    task = LearningTask(goal="vision", required_skills=["Biomedical Vision"], required_knowledge=["imaging physics"])
    gaps = detector.detect(task=task, graph=graph, source="tests")
    kinds = {(gap.gap_type, gap.subject) for gap in gaps}
    assert (GapType.MISSING_KNOWLEDGE, "imaging physics") in kinds
    assert (GapType.MISSING_SKILL, "ML") in kinds
    assert (GapType.MISSING_SKILL, "Python") not in kinds
    assert all(gap.evidence and gap.reason and gap.confidence is None for gap in gaps)
    assert all(gap.provenance.status == "PRESENT" for gap in gaps)
    failed = ExperienceRecord(task="build", kind=ExperienceKind.OBSERVED, outcome=LearningOutcome(success=False))
    others = detector.detect(experiences=[failed], prediction_uncertain=True, planning_failed=True, simulation_unavailable=True, research_evidence=["trial"], tool_gaps=["compiler"])
    types = {gap.gap_type for gap in others}
    assert types == {GapType.FAILED_VALIDATION, GapType.MISSING_EVIDENCE, GapType.HIGH_UNCERTAINTY, GapType.INSUFFICIENT_PRACTICE, GapType.MISSING_DOMAIN_CAPABILITY, GapType.MISSING_TOOL}
    assert detector.detect(task=LearningTask(goal="x", required_skills=["Unknown"]), graph=graph)[-1].gap_type == GapType.MISSING_SKILL
    assert any(gap.gap_type == GapType.MISSING_DOMAIN_CAPABILITY for gap in detector.detect(task=LearningTask(goal="x", required_skills=["Unknown"]), graph=graph))
    assert detector.detect(task=task)[0].provenance.status == "MISSING"


def test_experience_classification_and_lessons():
    evidence = LearningEvidence(statement="unit tests passed", kind=ExperienceKind.OBSERVED)
    observed = ExperienceRecord(task="sort", kind=ExperienceKind.OBSERVED, outcome=LearningOutcome(success=True), evidence=[evidence])
    simulated = ExperienceRecord(task="tank", kind=ExperienceKind.SIMULATED, outcome=LearningOutcome(success=False), plan="p1", constraint_violations=["level > 10"], prediction_error=0.4, uncertainty="wide interval", missing_skills=["control"], missing_knowledge=["fluid dynamics"])
    lessons = ExperienceAnalyzer().analyze([observed, simulated])
    kinds = {lesson.kind for lesson in lessons}
    assert kinds == set(LessonKind)
    success = [lesson for lesson in lessons if lesson.kind == LessonKind.SUCCESSFUL_PATTERN][0]
    assert success.status == "EVIDENCED" and success.generalized is False
    assert "One episode is not a general rule." in success.limitations
    sim_lessons = [lesson for lesson in lessons if lesson.experience_kind == ExperienceKind.SIMULATED]
    assert all(lesson.status == "PROPOSED" for lesson in sim_lessons)
    assert all("SIMULATED experience is not real-world experience." in lesson.limitations for lesson in sim_lessons)
    with pytest.raises(ValueError):
        ExperienceRecord(task="x", kind="MIXED")


def test_practice_engine_scores_only_when_computable():
    engine = PracticeEngine()
    task = PracticeTask(skill="arithmetic", prompt="2+2", expected="4")
    right = engine.problem(task, "4")
    wrong = engine.problem(task, "5")
    open_task = engine.problem(PracticeTask(skill="essay", prompt="write"), "text")
    assert right.passed and right.score == 1.0 and right.score_status == "COMPUTED"
    assert wrong.passed is False and wrong.errors
    assert open_task.passed is None and open_task.score is None and open_task.score_status == "NOT_EVALUABLE"
    code = engine.code("double", double, [((1,), 2), ((2,), 5)])
    assert code.score == 0.5 and code.passed is False
    assert engine.code("double", double, []).score_status == "NOT_EVALUABLE"
    crash = engine.code("div", lambda x: 1 / x, [((0,), 0)])
    assert "raised ZeroDivisionError" in crash.errors[0]
    research = engine.research("review", "claim", ["a"], ["a", "b"])
    assert research.score == 0.5 and research.errors == ["missing evidence: b"]
    assert engine.hypothesis("forecast", 1.0, None, 0.1).score_status == "NOT_EVALUABLE"
    near = engine.hypothesis("forecast", 1.0, 1.05, 0.1)
    assert near.passed and near.score_status == "COMPUTED_ABSOLUTE_ERROR"
    assert "Prediction is not knowledge." in near.limitations


def test_simulated_practice_is_labeled_and_not_real_world():
    engine = PracticeEngine()
    ok = engine.simulate("control", {"level": 1.0}, [{"level": 1.0}], target={"level": 2.0}, bounds={"level": (0.0, 5.0)})
    violated = engine.simulate("control", {"level": 4.0}, [{"level": 2.0}], bounds={"level": (0.0, 5.0)})
    unconstrained = engine.simulate("control", {"level": 1.0}, [{"level": 1.0}])
    unavailable = engine.simulate("control", {"level": 1.0}, [{"level": 1.0}], target={"level": 2.0}, backend=UnavailableSimulationBackend())
    assert ok.mode == PracticeMode.SIMULATED_PRACTICE and ok.passed
    assert ok.evidence[0].kind == ExperienceKind.SIMULATED
    assert "SIMULATED_PRACTICE is not real-world competence." in ok.limitations
    assert violated.passed is False and "outside" in violated.errors[0]
    assert unconstrained.score_status == "NOT_EVALUABLE"
    assert unavailable.passed is None and unavailable.score_status == "NOT_EVALUABLE"
    robot = engine.robot_navigation("nav", (0, 0), (2, 0), obstacles=((1, 0),), bounds=(4, 4))
    assert robot.passed and "No physical robot." in robot.limitations
    blocked = engine.robot_navigation("nav", (0, 0), (2, 0), obstacles=((1, 0), (0, 1)), bounds=(3, 3))
    assert blocked.passed is False and blocked.score_status == "NOT_EVALUABLE"


def test_assessment_uses_grounded_metrics():
    skill = Skill(name="double", skill_type=SkillType.PROGRAMMING)
    assessment = SkillAssessment().assess(skill, passing_code("double"), source="tests")
    metrics = {metric.name: metric for metric in assessment.metrics}
    assert assessment.status == AssessmentStatus.EVALUATED
    assert metrics["task_completion"].value == 1.0
    assert metrics["error_count"].value == 0
    assert metrics["evidence_coverage"].value == 1.0
    assert metrics["constraint_satisfaction"].status == "NOT_EVALUABLE"
    assert metrics["plan_validity"].status == "NOT_EVALUABLE"
    assert set(metrics) == {"task_completion", "constraint_satisfaction", "error_count", "evidence_coverage", "plan_validity"}
    declared = SkillAssessment().assess(Skill(name="x", skill_type=SkillType.KNOWLEDGE, status=SkillStatus.DECLARED), [])
    assert declared.status == AssessmentStatus.DECLARED
    assert SkillAssessment().assess(skill, [], observed=True).status == AssessmentStatus.OBSERVED
    assert SkillAssessment().assess(skill, []).status == AssessmentStatus.UNKNOWN
    open_attempt = PracticeEngine().problem(PracticeTask(skill="double", prompt="?"), "x")
    assert SkillAssessment().assess(skill, [open_attempt]).status == AssessmentStatus.PRACTICED
    assert "Assessment is not validation." in assessment.limitations


def test_validation_requires_explicit_criteria():
    validator = SkillValidator()
    skill = Skill(name="double", skill_type=SkillType.PROGRAMMING)
    one = validator.validate(skill, passing_code("double", 1), llm_claim="I have mastered this")
    assert one.validated is False
    assert any("LLM claim was ignored" in item for item in one.limitations)
    two = validator.validate(skill, passing_code("double"))
    assert two.validated is True
    assert "Validation is not universal competence." in two.limitations
    assert any("not real-world competence" in item for item in two.limitations)
    strict = ValidationCriteria(require_ground_truth=True, require_test_suite=True, require_constraint_satisfaction=True)
    missing = validator.validate(skill, passing_code("double"), strict)
    assert missing.validated is False and len(missing.reasons) == 3
    assert validator.validate(skill, passing_code("double"), strict, ground_truth_match=True, test_suite_passed=True, constraints_satisfied=True).validated
    observed_only = validator.validate(skill, passing_code("double"), ValidationCriteria(require_observed=True))
    assert observed_only.validated is False
    sim = [PracticeEngine().simulate("double", {"x": 0.0}, [{"x": 1.0}], target={"x": 1.0}) for _ in range(2)]
    assert validator.validate(skill, sim, ValidationCriteria(require_observed=True)).validated is False
    assert validator.validate(skill, []).validated is False


def test_learning_planner_orders_steps_as_proposal():
    graph = chain_graph()
    gaps = KnowledgeGapDetector().detect(task=LearningTask(goal="vision", required_skills=["Computer Vision"]), graph=graph)
    plan = LearningPlanner().plan("vision", gaps, graph=graph, effort={"ML": "caller estimate: 2 weeks"}, source="tests")
    assert [step.skill for step in plan.steps] == ["ML", "Deep Learning", "Computer Vision"]
    assert plan.status == "PROPOSAL" and plan.executed is False
    assert plan.steps[0].effort == "caller estimate: 2 weeks"
    assert plan.steps[1].effort is None
    assert plan.steps[2].prerequisites == ["Python", "ML", "Deep Learning"]
    assert plan.steps[0].validation.min_passing_episodes == 2
    empty = LearningPlanner().plan("nothing", [])
    assert empty.steps == [] and any("empty" in item for item in empty.limitations)
    with pytest.raises(PermissionError):
        LearningPlanner().plan("modify model weights", gaps)


def test_education_adapter_wraps_arc11():
    curriculum = Curriculum(name="cv", topics=[Topic(name="Python"), Topic(name="ML", prerequisites=["Python"]), Topic(name="Vision", prerequisites=["ML"])])
    student = StudentProfile(name="Sonjoy", declared_knowledge=["Python"])
    adapter = EducationLearningAdapter()
    graph = adapter.skill_graph(curriculum, student, source="tests")
    assert graph.order() == ["Python", "ML", "Vision"]
    assert graph.get_skill("Python").status == SkillStatus.DECLARED
    assert graph.get_skill("Vision").status == SkillStatus.PROPOSED
    objectives = adapter.objectives(student, curriculum, "vision")
    assert [item.skill for item in objectives] == ["ML", "Vision"]
    gaps = adapter.gaps(student, curriculum)
    assert all(gap.gap_type == GapType.MISSING_KNOWLEDGE and gap.evidence for gap in gaps)
    assert {gap.subject for gap in gaps} == {"Vision"}


def test_memory_integration_requires_consent_for_personal_context():
    memory = UniversalMemory()
    adapter = LearningMemoryAdapter(memory)
    record = ExperienceRecord(task="sorting practice", kind=ExperienceKind.SYNTHETIC, lesson="Merge sort passed supplied tests.", evidence=[LearningEvidence(statement="tests passed", kind=ExperienceKind.SYNTHETIC)], provenance=provenance("tests"))
    stored, evidence = adapter.store_experience(record)
    assert stored.metadata["experience_kind"] == "SYNTHETIC"
    assert stored.metadata["truth"] == "NOT_ASSERTED"
    assert evidence is not None and evidence.claim == "tests passed"
    assert memory.search("merge sort")
    with pytest.raises(PermissionError):
        adapter.store_experience(record, personal=True)
    with pytest.raises(PermissionError):
        adapter.store_experience(record, personal=True, consent=Consent(state=ConsentState.GRANTED, scope=["session"], persistent=False))
    personal = record.model_copy(update={"lesson": "Personal study goal: finish sorting chapter."})
    allowed, _ = adapter.store_experience(personal, personal=True, consent=Consent(state=ConsentState.GRANTED, scope=["persistent"], persistent=True))
    assert allowed.id != stored.id
    unsourced, no_evidence = adapter.store_experience(ExperienceRecord(task="x", kind=ExperienceKind.UNKNOWN))
    assert unsourced.metadata["provenance_status"] == "MISSING" and no_evidence is None


def test_personal_objectives_never_infer_sensitive_attributes():
    goals = [GoalManager().create("Finish thesis")]
    projects = [ProjectManager().create("Robot lab")]
    learning = [LearningManager().create("Linear algebra")]
    objectives = PersonalLearningAdapter().objectives(goals=goals, projects=projects, learning=learning, preferences=[Preference(key="study_time", value="morning")], source="user")
    assert [item.statement.split(":")[0] for item in objectives[:2]] == ["Goal", "Project"]
    assert objectives[2].skill == "Linear algebra"
    with pytest.raises(PermissionError):
        PersonalLearningAdapter().objectives(preferences=[Preference(key="health", value="x")])
    assert LearningSafetyPolicy().assess("infer health status from study logs")["allowed"] is False


def test_world_model_labels_are_not_facts():
    graph = KnowledgeGraph()
    skills = chain_graph()
    entities = WorldModelLearningAdapter().link_skills(graph, skills, source="tests")
    assert len(entities) == 5
    assert all(entity.epistemic != WorldEpistemic.OBSERVED for entity in entities)
    relations = graph.get_relations()
    assert len(relations) == 4 and all(item.epistemic == WorldEpistemic.HYPOTHESIZED for item in relations)
    ml = [entity for entity in entities if entity.name == "skill:ML"][0]
    note = WorldModelLearningAdapter().annotate(graph, ml, "practice", "passed in simulation", ExperienceKind.SIMULATED, source="tests")
    assert note.property.epistemic == WorldEpistemic.SIMULATED
    assert ml.properties == []
    predicted = WorldModelLearningAdapter().annotate(graph, ml, "forecast", "may pass", ExperienceKind.PREDICTED)
    assert predicted.property.epistemic == WorldEpistemic.PREDICTED


def test_cognitive_integration_consumes_state_without_rewriting():
    state = CognitivePipeline().run(CycleRequest(goal="Review a lab note", simulate=True, source="tests"), simulation_backend=UnavailableSimulationBackend())
    adapter = CognitiveLearningAdapter()
    gaps = adapter.gaps(state, source="tests")
    assert gaps[0].gap_type == GapType.MISSING_DOMAIN_CAPABILITY
    assert gaps[0].evidence == ["ARC-17 learning_update: simulation_backend_unavailable"]
    proposal = adapter.proposal(state)
    assert proposal.applied is False and proposal.status == LearningLifecycle.PROPOSED
    experiences = adapter.experiences(state)
    assert any(item.kind == ExperienceKind.SIMULATED for item in experiences)
    assert all(item.kind != ExperienceKind.OBSERVED for item in experiences if item.simulation_result)
    assert state.learning_update.applied is False
    assert state.executed is False


def test_adaptation_proposals_are_never_applied():
    service = AdaptationService()
    proposal = service.propose("skill_ordering", "Planning failed twice", ["episode-1", "episode-2"], expected_benefit="Earlier prerequisites", risk="Slower progress", source="tests")
    assert proposal.applied is False
    assert proposal.status == LearningLifecycle.AWAITING_HUMAN_APPROVAL
    assert proposal.validation_requirement and proposal.rollback_requirement
    with pytest.raises(PermissionError):
        service.apply(proposal)
    with pytest.raises(ValueError):
        service.propose("model_weights", "x", ["e"], expected_benefit="x", risk="x")
    with pytest.raises(ValueError):
        service.propose("planner_strategy", "x", [], expected_benefit="x", risk="x")
    with pytest.raises(PermissionError):
        service.propose("planner_strategy", "modify source code of the planner", ["e"], expected_benefit="x", risk="x")
    assert set(ADAPTATION_TARGETS) == {"planner_strategy", "retrieval_strategy", "skill_ordering", "practice_strategy", "domain_adapter", "tool_recommendation", "knowledge_source", "simulation_strategy"}


def test_transfer_and_cross_domain_reuse_keep_conflicts_visible():
    transfer = TransferService().propose("Grid Navigation", "Warehouse Routing", "shortest path search", assumptions=["discrete grid"], source="tests")
    assert isinstance(transfer, SkillTransferProposal)
    assert transfer.transfer_validated is False and transfer.status == "PROPOSAL"
    assert transfer.validation_requirements and transfer.risks and transfer.differences
    assert "A transfer proposal is not a transfer." in transfer.limitations
    capabilities = AgentCapabilityRegistry()
    register_learning_agents(AgentRegistry(), capabilities)
    reuse = CrossDomainSkillReuse(capabilities)
    report = reuse.compare("Path Planning", [SkillClaim(domain="robotics", skill="Path Planning", status=SkillStatus.VALIDATED), SkillClaim(domain="engineering", skill="Path Planning", status=SkillStatus.PROPOSED), SkillClaim(domain="biology", skill="Other", status=SkillStatus.UNKNOWN)])
    assert report.selected_winner is None
    assert "robotics=VALIDATED" in report.conflict and "engineering=PROPOSED" in report.conflict
    assert len(report.claims) == 2
    assert reuse.compare("Other", [SkillClaim(domain="biology", skill="Other", status=SkillStatus.UNKNOWN)]).conflict is None
    assert reuse.domains_for(["transfer"]) == ["learning"]
    assert CrossDomainSkillReuse().domains_for(["transfer"]) == []


def test_safety_policy_blocks_unsafe_and_allows_safe_learning():
    policy = LearningSafetyPolicy()
    for text in ("unsafe autonomous adaptation", "modify model weights", "modify source code", "permission escalation", "read credential store", "dangerous physical training on a physical robot", "malware execution", "weapon design", "clinical decision automation", "hidden personal data collection", "sensitive attribute inference"):
        assert policy.assess(text)["allowed"] is False, text
    for text in ("education practice on fractions", "simulation practice for tank control", "research learning about enzymes", "engineering practice with beams", "safe coding exercise", "knowledge organization", "human-reviewed adaptation proposal"):
        assert policy.assess(text)["allowed"] is True, text
    with pytest.raises(PermissionError):
        policy.guard("train malware")
    with pytest.raises(PermissionError):
        SkillGraph().add_skill(Skill(name="weapon assembly", skill_type=SkillType.ENGINEERING))


def test_provenance_tracks_missing_sources():
    assert provenance("lab notebook").status == "PRESENT"
    assert provenance(None).status == "MISSING"
    assert provenance("  ").status == "MISSING"
    attempt = PracticeEngine().problem(PracticeTask(skill="a", prompt="1", expected="1"), "1")
    assert attempt.provenance.status == "MISSING"
    sourced = TransferService().propose("a", "b", "c", source="tests")
    assert sourced.provenance.source == "tests"
    adaptation = AdaptationService().propose("knowledge_source", "gap", ["e1"], expected_benefit="x", risk="y")
    assert adaptation.provenance.status == "MISSING" and adaptation.provenance.evidence_refs == ["e1"]
    gaps = KnowledgeGapDetector().detect(tool_gaps=["compiler"], source="tests")
    assert gaps[0].provenance.agent == "knowledge_gap_detector"


def test_pipeline_requires_human_approval_for_updates():
    graph = chain_graph(declared=("Python", "ML", "Deep Learning", "Computer Vision"))
    request = LearningRequest(task=LearningTask(goal="biomedical vision", required_skills=["Biomedical Vision"]), attempts=passing_code("Biomedical Vision"), source="tests")
    waiting = LearningPipeline().run(request, graph=graph)
    assert waiting.lifecycle == LearningLifecycle.AWAITING_HUMAN_APPROVAL
    assert waiting.updates[0].applied is False
    assert graph.get_skill("Biomedical Vision").status == SkillStatus.PROPOSED
    assert waiting.executed is False
    approved = LearningPipeline().run(request.model_copy(update={"human_approved": True}), graph=graph)
    assert approved.lifecycle == LearningLifecycle.UPDATED
    assert approved.updates[0].applied is True and approved.updates[0].human_approval is True
    assert graph.get_skill("Biomedical Vision").status == SkillStatus.VALIDATED
    assert approved.history[-3:] == [LearningLifecycle.READY_FOR_UPDATE, LearningLifecycle.AWAITING_HUMAN_APPROVAL, LearningLifecycle.UPDATED]


def test_pipeline_failure_handling():
    rejected = LearningPipeline().run(LearningRequest(task=LearningTask(goal="modify model weights automatically")))
    assert rejected.lifecycle == LearningLifecycle.REJECTED and "safety" in rejected.failure
    nothing = LearningPipeline().run(LearningRequest(task=LearningTask(goal="nothing to learn")))
    assert nothing.lifecycle == LearningLifecycle.REJECTED and "No evidenced gap" in nothing.failure
    one = LearningPipeline().run(LearningRequest(task=LearningTask(goal="x", required_skills=["Sorting"]), attempts=passing_code("Sorting", 1)))
    assert one.lifecycle == LearningLifecycle.REJECTED and "Validation criteria" in one.failure
    assert one.assessments[0].status == AssessmentStatus.EVALUATED
    bad_graph = SkillGraph()
    bad_graph.add_skill(Skill(name="A", skill_type=SkillType.KNOWLEDGE))
    bad_graph._requires["a"].add("ghost")
    failed = LearningPipeline().run(LearningRequest(task=LearningTask(goal="x", required_skills=["A"])), graph=bad_graph)
    assert failed.lifecycle == LearningLifecycle.FAILED and failed.failure


def test_agent_registration_uses_unique_names():
    from superagi.cognition import register_cognition_agents
    from superagi.collaboration.registration import register_collaboration_agents
    from superagi.engineering.registration import register_engineering_agents
    from superagi.evolution.registration import register_evolution_agents
    from superagi.learning.agents import AGENT_CLASSES, AdaptationAgent, LearningCoordinatorAgent, PracticeAgent, TransferAgent, ValidationAgent
    from superagi.world_model.registration import register_world_model_agents

    registry = AgentRegistry()
    capabilities = AgentCapabilityRegistry()
    for register in (register_evolution_agents, register_world_model_agents, register_cognition_agents, register_collaboration_agents, register_engineering_agents):
        register(registry, capabilities)
    created = register_learning_agents(registry, capabilities)
    assert len(created) == len(AGENT_CLASSES) == 8
    assert len(capabilities.discover(["learning"], domain="learning")) == 8
    assert all(item.capability.domain == "learning" for item in learning_descriptors())
    assert all(agent.metadata.name.startswith("learning_") for agent in created)
    coordinator = run_agent(LearningCoordinatorAgent(), request=LearningRequest(task=LearningTask(goal="x", required_skills=["Sorting"])))
    assert coordinator.output["executed"] is False and coordinator.output["lifecycle"] == "REJECTED"
    practice = run_agent(PracticeAgent(), skill_name="control", initial={"x": 0.0}, steps=[{"x": 1.0}], target={"x": 1.0})
    assert practice.output["mode"] == "SIMULATED_PRACTICE" and practice.output["passed"] is True
    validation = run_agent(ValidationAgent(), attempts=passing_code("x", 1))
    assert validation.output["validated"] is False
    adaptation = run_agent(AdaptationAgent(), evidence=["e1"])
    assert adaptation.output["applied"] is False
    transfer = run_agent(TransferAgent(), source_skill="a", target_skill="b")
    assert transfer.output["transfer_validated"] is False


def test_demos_are_honest():
    programming = load_demo("programming_skill_demo.py").build()
    research = load_demo("research_skill_demo.py").build()
    engineering = load_demo("engineering_skill_demo.py").build()
    robot = load_demo("robot_navigation_skill_demo.py").build()
    adaptive = load_demo("adaptive_proposal_demo.py").build()
    for report in (programming, research, engineering, robot, adaptive):
        assert report["executed"] is False
        assert "PROPOSAL ONLY" in report["banner"] and "MOCK / DETERMINISTIC" in report["banner"]
        assert "NO REAL-WORLD AUTONOMOUS ADAPTATION" in report["banner"]
    assert "SIMULATION ONLY" in engineering["banner"] and "SIMULATION ONLY" in robot["banner"]
    assert programming["lifecycle"] == "AWAITING_HUMAN_APPROVAL" and programming["update_applied"] == [False]
    assert research["plan_status"] == "PROPOSAL" and research["coverage"] == [0.5, 1.0]
    assert engineering["validated_in_simulation"] is True and engineering["validated_for_real_world"] is False
    assert robot["passed"] == [True, True, False] and robot["physical_robot"] is False
    assert adaptive["adaptation_applied"] is False and adaptive["apply_attempt"].startswith("refused")
