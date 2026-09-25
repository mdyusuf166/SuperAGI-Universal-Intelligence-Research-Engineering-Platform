from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..query import WorldQuery


class WorldQueryAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="world_query_agent", description="Deterministic world-model queries", capabilities=("world_query", "world_model"), risk_level="low"))

    async def run(self, task, context):
        query = WorldQuery(context.values["graph"], context.values.get("timeline"))
        name = context.values.get("name", "")
        hits = query.find_entity(name)
        return AgentResult(success=True, confidence=0.3, summary="Query result. Unknown stays unknown.", output={"agent": self.metadata.name, "labels": [hit.label for hit in hits], "epistemic": [hit.epistemic.value for hit in hits], "executed": False}, limitations=["Query does not create facts."])
