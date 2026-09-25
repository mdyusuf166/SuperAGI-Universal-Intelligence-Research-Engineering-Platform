from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..communication import CommunicationSupport


class CommunicationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="communication_agent", description="Summaries limited to supplied artifacts", capabilities=("collaboration", "communication"), risk_level="low"))

    async def run(self, task, context):
        summary = CommunicationSupport().summarize(meetings=context.values.get("meetings"), tasks=context.values.get("tasks"), project=context.values.get("project"), research=context.values.get("research"), engineering=context.values.get("engineering"), decisions=context.values.get("decisions"), participants=context.values.get("participants"), evidence=context.values.get("evidence"), sources=context.values.get("sources"))
        return AgentResult(success=summary["fabricated"] is False, confidence=0.4, summary="Summary of supplied artifacts only.", output={"agent": self.metadata.name, **summary}, limitations=["Missing sections stay marked as not provided."])
