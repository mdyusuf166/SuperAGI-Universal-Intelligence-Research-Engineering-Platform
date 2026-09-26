"""Learning pipeline. Consequential updates always wait for human review."""

from __future__ import annotations

from pydantic import Field

from .assessment import SkillAssessment, SkillValidator
from .experience import ExperienceAnalyzer
from .gaps import KnowledgeGapDetector
from .curriculum import LearningPlanner
from .models import ExperienceRecord, KnowledgeGap, LearningAssessment, LearningLifecycle, LearningPlan, LearningTask, LearningUpdate, Lesson, LM, PracticeAttempt, Provenance, Skill, SkillStatus, SkillType, ValidationCriteria, ValidationResult
from .provenance import LearningStateMachine, provenance
from .safety import LearningSafetyPolicy
from .skills import SkillGraph


class LearningRequest(LM):
    task: LearningTask
    known: list[str] = Field(default_factory=list)
    experiences: list[ExperienceRecord] = Field(default_factory=list)
    extra_gaps: list[KnowledgeGap] = Field(default_factory=list)
    attempts: list[PracticeAttempt] = Field(default_factory=list)
    criteria: ValidationCriteria = Field(default_factory=ValidationCriteria)
    ground_truth_match: bool | None = None
    test_suite_passed: bool | None = None
    constraints_satisfied: bool | None = None
    effort: dict[str, str] = Field(default_factory=dict)
    human_approved: bool = False
    source: str | None = None


class LearningResult(LM):
    lifecycle: LearningLifecycle
    history: list[LearningLifecycle]
    lessons: list[Lesson] = Field(default_factory=list)
    gaps: list[KnowledgeGap] = Field(default_factory=list)
    plan: LearningPlan | None = None
    attempts: list[PracticeAttempt] = Field(default_factory=list)
    assessments: list[LearningAssessment] = Field(default_factory=list)
    validations: list[ValidationResult] = Field(default_factory=list)
    updates: list[LearningUpdate] = Field(default_factory=list)
    safety: dict = Field(default_factory=dict)
    provenance: Provenance
    failure: str | None = None
    executed: bool = False
    limitations: list[str] = Field(default_factory=list)


LIMITS = [
    "MOCK / DETERMINISTIC.",
    "PROPOSAL ONLY: no model weights, source code, permissions, or policies were changed.",
    "Practice is not mastery. Validation holds only for the stated criteria.",
    "NO REAL-WORLD AUTONOMOUS ADAPTATION.",
]


class LearningPipeline:
    def __init__(self) -> None:
        self.safety = LearningSafetyPolicy()

    def run(self, request: LearningRequest, *, graph: SkillGraph | None = None) -> LearningResult:
        machine = LearningStateMachine()
        record = provenance(request.source, agent="learning_pipeline")
        safety = self.safety.assess(request.task.goal)
        partial: dict = {"safety": safety}

        def finish(state: LearningLifecycle, failure: str | None = None) -> LearningResult:
            if state != machine.state:
                machine.move(state)
            return LearningResult(lifecycle=machine.state, history=list(machine.history), provenance=record, failure=failure, limitations=LIMITS, **partial)

        if not safety["allowed"]:
            return finish(LearningLifecycle.REJECTED, "Learning safety policy rejected the goal")
        try:
            graph = graph or SkillGraph()
            partial["lessons"] = ExperienceAnalyzer().analyze(request.experiences)
            gaps = KnowledgeGapDetector().detect(task=request.task, graph=graph, known=request.known, experiences=request.experiences, source=request.source) + list(request.extra_gaps)
            partial["gaps"] = gaps
            if not gaps:
                return finish(LearningLifecycle.REJECTED, "No evidenced gap or explicit requirement was found")
            machine.move(LearningLifecycle.PROPOSED)
            plan = LearningPlanner().plan(request.task.goal, gaps, graph=graph, effort=request.effort, criteria=request.criteria, source=request.source)
            partial["plan"] = plan
            machine.move(LearningLifecycle.PLANNED)
            machine.move(LearningLifecycle.PRACTICING)
            partial["attempts"] = list(request.attempts)
            machine.move(LearningLifecycle.ASSESSING)
            assessments, validations = [], []
            for step in plan.steps:
                skill = self._skill(graph, step.skill)
                attempts = [item for item in request.attempts if item.skill.casefold() == step.skill.casefold()]
                assessments.append(SkillAssessment().assess(skill, attempts, source=request.source))
                validations.append(SkillValidator().validate(skill, attempts, request.criteria, ground_truth_match=request.ground_truth_match, test_suite_passed=request.test_suite_passed, constraints_satisfied=request.constraints_satisfied))
            partial["assessments"] = assessments
            machine.move(LearningLifecycle.VALIDATING)
            partial["validations"] = validations
            validated = [item for item in validations if item.validated]
            if not validated:
                return finish(LearningLifecycle.REJECTED, "Validation criteria were not met; no update is proposed")
            machine.move(LearningLifecycle.READY_FOR_UPDATE)
            machine.move(LearningLifecycle.AWAITING_HUMAN_APPROVAL)
            updates = [LearningUpdate(skill=item.skill, proposed_status=SkillStatus.VALIDATED, provenance=record, limitations=list(item.limitations) + ["Updates only the skill record, never a model or code."]) for item in validated]
            if not request.human_approved:
                partial["updates"] = updates
                return finish(LearningLifecycle.AWAITING_HUMAN_APPROVAL)
            applied = []
            for update in updates:
                try:
                    graph.get_skill(update.skill).status = SkillStatus.VALIDATED
                except KeyError:
                    pass
                applied.append(update.model_copy(update={"status": LearningLifecycle.UPDATED, "applied": True, "human_approval": True}))
            partial["updates"] = applied
            return finish(LearningLifecycle.UPDATED)
        except (ValueError, KeyError, PermissionError) as exc:
            if machine.state in {LearningLifecycle.UPDATED, LearningLifecycle.REJECTED, LearningLifecycle.FAILED, LearningLifecycle.AWAITING_HUMAN_APPROVAL}:
                raise
            return finish(LearningLifecycle.FAILED, str(exc))

    def _skill(self, graph: SkillGraph, name: str) -> Skill:
        try:
            return graph.get_skill(name)
        except KeyError:
            return Skill(name=name, skill_type=SkillType.KNOWLEDGE, status=SkillStatus.UNKNOWN)
