from superagi.core.models import AgentContext, AgentResult, Task
from superagi.research.hypotheses import HypothesisGenerator
from superagi.research.models import ResearchQuestion

from ._base import ResearchAgent, metadata


class HypothesisAgent(ResearchAgent):
    def __init__(self) -> None:
        super().__init__(metadata("hypothesis_agent", "Generates explicitly unproven hypotheses", ("hypothesis_generation",)))
        self.generator = HypothesisGenerator()

    def generate(self, question: ResearchQuestion, evidence_ids=()):
        return self.generator.generate(question, evidence_ids)

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        question = context.values["research_question"]
        hypotheses = self.generate(ResearchQuestion.model_validate(question), context.values.get("evidence_ids", ()))
        return AgentResult(success=True, confidence=0.5, summary="Generated proposed hypotheses; no experimental validation occurred", output={"hypotheses": [item.model_dump() for item in hypotheses]})
