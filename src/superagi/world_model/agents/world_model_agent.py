from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult


class WorldModelAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="universal_world_model_agent", description="Registers typed world-model entities", capabilities=("world_model",), risk_level="low"))

    async def run(self, task, context):
        from ..graph import KnowledgeGraph

        graph = context.values.get("graph") or KnowledgeGraph()
        for entity in context.values.get("entities", []):
            graph.add_entity(entity)
        return AgentResult(success=True, confidence=0.3, summary="World model entities registered. Not verified facts.", output={"agent": self.metadata.name, "count": len(graph.entities()), "names": [entity.name for entity in graph.entities()], "executed": False}, limitations=["Registration is not verification."])
