from superagi.core.models import AgentContext, AgentResult, Task
from superagi.research.experiments import ExperimentDesigner
from superagi.research.hypotheses import Hypothesis
from superagi.research.models import ResearchQuestion

from ._base import ResearchAgent, metadata


class ExperimentAgent(ResearchAgent):
    def __init__(self) -> None:
        super().__init__(metadata("experiment_agent", "Designs non-executing experiment proposals", ("experiment_design", "reproducibility")))
        self.designer = ExperimentDesigner()

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        proposal = self.designer.design(ResearchQuestion.model_validate(context.values["research_question"]), Hypothesis.model_validate(context.values["hypotheses"][0]))
        return AgentResult(success=True, confidence=0.7, summary="Produced a proposal only; no physical experiment was executed", output={"experiment": proposal.model_dump()})
