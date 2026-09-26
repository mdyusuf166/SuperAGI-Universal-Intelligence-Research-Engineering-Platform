"""ARC-01 agents for learning. Every output is a proposal."""

from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from .adaptation import AdaptationService, TransferService
from .assessment import SkillAssessment, SkillValidator
from .gaps import KnowledgeGapDetector
from .models import LearningTask, Skill, SkillStatus, SkillType
from .pipeline import LearningPipeline, LearningRequest
from .practice import PracticeEngine
from .skills import SkillGraph


def _result(agent, summary: str, output: dict) -> AgentResult:
    output = {"agent": agent, "executed": False, **output}
    return AgentResult(success=True, confidence=0.3, summary=summary, output=output, limitations=["Proposal only. Practice is not mastery. No real-world execution."])


def _skill(values, default: str) -> Skill:
    return values.get("skill") or Skill(name=values.get("skill_name", default), skill_type=values.get("skill_type", SkillType.KNOWLEDGE), status=SkillStatus.UNKNOWN)


class LearningCoordinatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_coordinator_agent", description="Runs the learning pipeline as a proposal", capabilities=("learning",), risk_level="low"))

    async def run(self, task, context):
        request = context.values.get("request") or LearningRequest(task=LearningTask(goal=task.description))
        result = LearningPipeline().run(request, graph=context.values.get("graph"))
        return _result(self.metadata.name, "Learning pipeline finished.", {"lifecycle": result.lifecycle.value, "gaps": len(result.gaps)})


class KnowledgeGapAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_gap_agent", description="Detects evidenced knowledge gaps", capabilities=("learning", "knowledge_gap"), risk_level="low"))

    async def run(self, task, context):
        gaps = KnowledgeGapDetector().detect(task=context.values.get("task"), graph=context.values.get("graph"), known=context.values.get("known", []), experiences=context.values.get("experiences", []), source=context.values.get("source"))
        return _result(self.metadata.name, "Gap detection.", {"gaps": [gap.gap_type.value for gap in gaps]})


class SkillAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_skill_agent", description="Validates a skill graph structure", capabilities=("learning", "skill_graph"), risk_level="low"))

    async def run(self, task, context):
        graph = context.values.get("graph") or SkillGraph()
        return _result(self.metadata.name, "Skill graph check.", {"issues": graph.validate(), "order": graph.order()})


class PracticeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_practice_agent", description="Runs deterministic or simulated practice", capabilities=("learning", "practice"), risk_level="low"))

    async def run(self, task, context):
        values = context.values
        attempt = PracticeEngine().simulate(values.get("skill_name", "practice"), values.get("initial", {"x": 0.0}), values.get("steps", [{"x": 1.0}]), target=values.get("target"), bounds=values.get("bounds"), source=values.get("source"))
        return _result(self.metadata.name, "Practice attempt.", {"mode": attempt.mode.value, "passed": attempt.passed, "score_status": attempt.score_status})


class AssessmentAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_assessment_agent", description="Assesses practice with grounded metrics", capabilities=("learning", "assessment"), risk_level="low"))

    async def run(self, task, context):
        result = SkillAssessment().assess(_skill(context.values, task.description), context.values.get("attempts", []))
        return _result(self.metadata.name, "Assessment.", {"status": result.status.value})


class ValidationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_validation_agent", description="Validates a skill against explicit criteria", capabilities=("learning", "validation"), risk_level="low"))

    async def run(self, task, context):
        result = SkillValidator().validate(_skill(context.values, task.description), context.values.get("attempts", []), context.values.get("criteria"))
        return _result(self.metadata.name, "Validation.", {"validated": result.validated, "reasons": result.reasons})


class AdaptationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_adaptation_agent", description="Proposes adaptations that require human approval", capabilities=("learning", "adaptation"), risk_level="low"))

    async def run(self, task, context):
        values = context.values
        proposal = AdaptationService().propose(values.get("target", "practice_strategy"), values.get("reason", task.description), values.get("evidence", ["caller request"]), expected_benefit=values.get("expected_benefit", "Not measured."), risk=values.get("risk", "Unknown."), source=values.get("source"))
        return _result(self.metadata.name, "Adaptation proposal.", {"applied": proposal.applied, "status": proposal.status.value})


class TransferAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="learning_transfer_agent", description="Proposes skill transfer without claiming success", capabilities=("learning", "transfer"), risk_level="low"))

    async def run(self, task, context):
        values = context.values
        proposal = TransferService().propose(values["source_skill"], values["target_skill"], values.get("shared_abstraction", "unspecified"), source=values.get("source"))
        return _result(self.metadata.name, "Transfer proposal.", {"transfer_validated": proposal.transfer_validated, "status": proposal.status})


AGENT_CLASSES = (
    LearningCoordinatorAgent,
    KnowledgeGapAgent,
    SkillAgent,
    PracticeAgent,
    AssessmentAgent,
    ValidationAgent,
    AdaptationAgent,
    TransferAgent,
)
