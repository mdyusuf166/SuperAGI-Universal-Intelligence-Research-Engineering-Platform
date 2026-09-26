"""Typed learning, skill, and adaptation records."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LM(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LearningLifecycle(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    PROPOSED = "PROPOSED"
    PLANNED = "PLANNED"
    PRACTICING = "PRACTICING"
    ASSESSING = "ASSESSING"
    VALIDATING = "VALIDATING"
    READY_FOR_UPDATE = "READY_FOR_UPDATE"
    AWAITING_HUMAN_APPROVAL = "AWAITING_HUMAN_APPROVAL"
    UPDATED = "UPDATED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class SkillType(str, Enum):
    KNOWLEDGE = "KNOWLEDGE"
    REASONING = "REASONING"
    PLANNING = "PLANNING"
    SIMULATION = "SIMULATION"
    PREDICTION = "PREDICTION"
    RESEARCH = "RESEARCH"
    PROGRAMMING = "PROGRAMMING"
    ENGINEERING = "ENGINEERING"
    BIOMEDICAL = "BIOMEDICAL"
    ROBOTICS = "ROBOTICS"
    CYBERSECURITY = "CYBERSECURITY"
    QUANTUM = "QUANTUM"
    COMMUNICATION = "COMMUNICATION"
    COLLABORATION = "COLLABORATION"
    EDUCATION = "EDUCATION"


class SkillStatus(str, Enum):
    DECLARED = "DECLARED"
    PROPOSED = "PROPOSED"
    PRACTICED = "PRACTICED"
    EVALUATED = "EVALUATED"
    VALIDATED = "VALIDATED"
    UNKNOWN = "UNKNOWN"


class SkillLevel(str, Enum):
    UNASSESSED = "UNASSESSED"
    INTRODUCED = "INTRODUCED"
    PRACTICED = "PRACTICED"
    VALIDATED_FOR_CRITERIA = "VALIDATED_FOR_CRITERIA"


class AssessmentStatus(str, Enum):
    DECLARED = "DECLARED"
    OBSERVED = "OBSERVED"
    PRACTICED = "PRACTICED"
    EVALUATED = "EVALUATED"
    VALIDATED = "VALIDATED"
    UNKNOWN = "UNKNOWN"


class GapType(str, Enum):
    MISSING_KNOWLEDGE = "MISSING_KNOWLEDGE"
    MISSING_SKILL = "MISSING_SKILL"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    INSUFFICIENT_PRACTICE = "INSUFFICIENT_PRACTICE"
    HIGH_UNCERTAINTY = "HIGH_UNCERTAINTY"
    FAILED_VALIDATION = "FAILED_VALIDATION"
    MISSING_TOOL = "MISSING_TOOL"
    MISSING_DOMAIN_CAPABILITY = "MISSING_DOMAIN_CAPABILITY"


class ExperienceKind(str, Enum):
    OBSERVED = "OBSERVED"
    SIMULATED = "SIMULATED"
    PREDICTED = "PREDICTED"
    SYNTHETIC = "SYNTHETIC"
    UNKNOWN = "UNKNOWN"


class LessonKind(str, Enum):
    SUCCESSFUL_PATTERN = "SUCCESSFUL_PATTERN"
    FAILED_PATTERN = "FAILED_PATTERN"
    CONSTRAINT_VIOLATION = "CONSTRAINT_VIOLATION"
    PREDICTION_ERROR = "PREDICTION_ERROR"
    PLANNING_WEAKNESS = "PLANNING_WEAKNESS"
    MISSING_KNOWLEDGE = "MISSING_KNOWLEDGE"
    MISSING_SKILL = "MISSING_SKILL"
    UNCERTAINTY = "UNCERTAINTY"


class PracticeMode(str, Enum):
    DETERMINISTIC_PRACTICE = "DETERMINISTIC_PRACTICE"
    SIMULATED_PRACTICE = "SIMULATED_PRACTICE"


class Provenance(LM):
    source: str | None = None
    status: str = "MISSING"
    agent: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class LearningEvidence(LM):
    id: UUID = Field(default_factory=uuid4)
    statement: str = Field(min_length=1)
    kind: ExperienceKind = ExperienceKind.UNKNOWN
    status: str = "SUPPLIED"
    provenance: Provenance = Field(default_factory=Provenance)


class SkillPrerequisite(LM):
    skill: str
    required: str


class SkillDependency(LM):
    skill: str
    depends_on: list[str] = Field(default_factory=list)


class SkillEvidence(LM):
    id: UUID = Field(default_factory=uuid4)
    skill: str
    statement: str
    kind: ExperienceKind
    passed: bool | None = None
    provenance: Provenance = Field(default_factory=Provenance)


class SkillVersion(LM):
    number: int = 0
    note: str = "initial proposal"


class Skill(LM):
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(min_length=1)
    skill_type: SkillType
    status: SkillStatus = SkillStatus.UNKNOWN
    level: SkillLevel = SkillLevel.UNASSESSED
    domain: str = ""
    evidence: list[SkillEvidence] = Field(default_factory=list)
    version: SkillVersion = Field(default_factory=SkillVersion)
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=lambda: ["A recorded skill is not real-world competence."])


class LearningObjective(LM):
    id: UUID = Field(default_factory=uuid4)
    statement: str = Field(min_length=1)
    skill: str | None = None
    status: LearningLifecycle = LearningLifecycle.PROPOSED
    provenance: Provenance = Field(default_factory=Provenance)


class LearningTask(LM):
    id: UUID = Field(default_factory=uuid4)
    goal: str = Field(min_length=1)
    required_skills: list[str] = Field(default_factory=list)
    required_knowledge: list[str] = Field(default_factory=list)
    status: LearningLifecycle = LearningLifecycle.IDENTIFIED
    provenance: Provenance = Field(default_factory=Provenance)


class LearningOutcome(LM):
    id: UUID = Field(default_factory=uuid4)
    success: bool | None = None
    statement: str = ""
    kind: ExperienceKind = ExperienceKind.UNKNOWN
    status: str = "SUPPLIED"
    provenance: Provenance = Field(default_factory=Provenance)


class ExperienceRecord(LM):
    id: UUID = Field(default_factory=uuid4)
    task: str = Field(min_length=1)
    kind: ExperienceKind
    context: str = ""
    observation: str = ""
    action_proposal: str = ""
    simulation_result: str | None = None
    prediction: str | None = None
    plan: str | None = None
    outcome: LearningOutcome = Field(default_factory=LearningOutcome)
    evaluation: str = ""
    lesson: str = ""
    constraint_violations: list[str] = Field(default_factory=list)
    prediction_error: float | None = None
    uncertainty: str | None = None
    missing_skills: list[str] = Field(default_factory=list)
    missing_knowledge: list[str] = Field(default_factory=list)
    evidence: list[LearningEvidence] = Field(default_factory=list)
    status: str = "RECORDED"
    provenance: Provenance = Field(default_factory=Provenance)


LearningExperience = ExperienceRecord


class LearningEpisode(LM):
    id: UUID = Field(default_factory=uuid4)
    experiences: list[ExperienceRecord] = Field(default_factory=list)
    status: str = "RECORDED"
    provenance: Provenance = Field(default_factory=Provenance)


class Lesson(LM):
    id: UUID = Field(default_factory=uuid4)
    kind: LessonKind
    statement: str
    status: str = "PROPOSED"
    experience_kind: ExperienceKind
    evidence_refs: list[str] = Field(default_factory=list)
    generalized: bool = False
    limitations: list[str] = Field(default_factory=list)


class KnowledgeGap(LM):
    id: UUID = Field(default_factory=uuid4)
    gap_type: GapType
    subject: str
    reason: str
    evidence: list[str] = Field(default_factory=list)
    confidence: float | None = None
    confidence_basis: str = "No confidence was supplied."
    status: LearningLifecycle = LearningLifecycle.IDENTIFIED
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class LearningProposal(LM):
    id: UUID = Field(default_factory=uuid4)
    gaps: list[KnowledgeGap] = Field(default_factory=list)
    statement: str
    status: LearningLifecycle = LearningLifecycle.PROPOSED
    applied: bool = False
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class ValidationCriteria(LM):
    min_passing_episodes: int = Field(default=2, ge=2)
    require_ground_truth: bool = False
    require_test_suite: bool = False
    require_constraint_satisfaction: bool = False
    require_observed: bool = False


class LearningStep(LM):
    id: UUID = Field(default_factory=uuid4)
    skill: str
    prerequisites: list[str] = Field(default_factory=list)
    practice_task: str
    assessment_criteria: list[str] = Field(default_factory=list)
    validation: ValidationCriteria = Field(default_factory=ValidationCriteria)
    effort: str | None = None
    status: LearningLifecycle = LearningLifecycle.PLANNED


class LearningPlan(LM):
    id: UUID = Field(default_factory=uuid4)
    goal: str
    steps: list[LearningStep] = Field(default_factory=list)
    status: str = "PROPOSAL"
    executed: bool = False
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class PracticeTask(LM):
    id: UUID = Field(default_factory=uuid4)
    skill: str
    prompt: str
    expected: str | None = None
    kind: str = "problem"


class PracticeAttempt(LM):
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    skill: str
    mode: PracticeMode
    attempt: str
    result: str
    passed: bool | None = None
    errors: list[str] = Field(default_factory=list)
    feedback: str = ""
    score: float | None = None
    score_status: str = "NOT_EVALUABLE"
    evidence: list[SkillEvidence] = Field(default_factory=list)
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class AssessmentMetric(LM):
    name: str
    status: str
    value: float | None = None
    detail: str = ""


class LearningAssessment(LM):
    id: UUID = Field(default_factory=uuid4)
    skill: str
    status: AssessmentStatus
    metrics: list[AssessmentMetric] = Field(default_factory=list)
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class ValidationResult(LM):
    skill: str
    validated: bool
    reasons: list[str] = Field(default_factory=list)
    criteria: ValidationCriteria
    limitations: list[str] = Field(default_factory=list)


class LearningUpdate(LM):
    id: UUID = Field(default_factory=uuid4)
    skill: str
    proposed_status: SkillStatus
    status: LearningLifecycle = LearningLifecycle.AWAITING_HUMAN_APPROVAL
    applied: bool = False
    human_approval: bool = False
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class AdaptationProposal(LM):
    id: UUID = Field(default_factory=uuid4)
    target: str
    reason: str
    evidence: list[str] = Field(default_factory=list)
    expected_benefit: str
    risk: str
    validation_requirement: str
    rollback_requirement: str
    status: LearningLifecycle = LearningLifecycle.AWAITING_HUMAN_APPROVAL
    applied: bool = False
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class SkillTransferProposal(LM):
    id: UUID = Field(default_factory=uuid4)
    source_skill: str
    target_skill: str
    shared_abstraction: str
    assumptions: list[str] = Field(default_factory=list)
    differences: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    validation_requirements: list[str] = Field(default_factory=list)
    status: str = "PROPOSAL"
    transfer_validated: bool = False
    provenance: Provenance = Field(default_factory=Provenance)
    limitations: list[str] = Field(default_factory=list)


class SkillClaim(LM):
    domain: str
    skill: str
    status: SkillStatus
    statement: str = ""


class SkillReuseReport(LM):
    skill: str
    claims: list[SkillClaim]
    conflict: str | None = None
    selected_winner: str | None = None
