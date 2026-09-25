from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..evaluation import EvolutionReview


class EvolutionReviewAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="evolution_review_agent", description="Reviews evolution proposals without applying them", capabilities=("evolution_review", "evolution"), risk_level="low"))

    async def run(self, task, context):
        report = EvolutionReview().review(context.values["proposal"])
        return AgentResult(success=report["accepted"], confidence=0.3, summary="Evolution review. No change was applied.", output={"agent": self.metadata.name, "status": report["status"], "accepted": report["accepted"], "findings": [item.model_dump() for item in report["findings"]]}, limitations=["Review is not permission to modify the system."])
