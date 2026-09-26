"""ARC-18 learning, skill acquisition, and adaptation proposals.

Practice is not mastery. Simulated practice is not real-world competence.
Nothing here changes model weights, source code, permissions, or policies.
"""

from .adaptation import ADAPTATION_TARGETS, AdaptationService, CrossDomainSkillReuse, TransferService
from .assessment import SkillAssessment, SkillValidator
from .curriculum import EducationLearningAdapter, LearningPlanner
from .experience import ExperienceAnalyzer
from .gaps import KnowledgeGapDetector
from .integration import CognitiveLearningAdapter, LearningMemoryAdapter, PersonalLearningAdapter, WorldModelLearningAdapter
from .models import (
    AdaptationProposal,
    AssessmentMetric,
    AssessmentStatus,
    ExperienceKind,
    ExperienceRecord,
    GapType,
    KnowledgeGap,
    LearningAssessment,
    LearningEpisode,
    LearningEvidence,
    LearningExperience,
    LearningLifecycle,
    LearningObjective,
    LearningOutcome,
    LearningPlan,
    LearningProposal,
    LearningStep,
    LearningTask,
    LearningUpdate,
    Lesson,
    LessonKind,
    PracticeAttempt,
    PracticeMode,
    PracticeTask,
    Skill,
    SkillClaim,
    SkillDependency,
    SkillEvidence,
    SkillLevel,
    SkillPrerequisite,
    SkillReuseReport,
    SkillStatus,
    SkillTransferProposal,
    SkillType,
    SkillVersion,
    ValidationCriteria,
    ValidationResult,
)
from .pipeline import LearningPipeline, LearningRequest, LearningResult
from .practice import PracticeEngine
from .provenance import LearningStateMachine, provenance
from .registration import learning_descriptors, register_learning_agents
from .safety import LearningSafetyPolicy
from .skills import SkillGraph

__all__ = [name for name in dir() if not name.startswith("_")]
