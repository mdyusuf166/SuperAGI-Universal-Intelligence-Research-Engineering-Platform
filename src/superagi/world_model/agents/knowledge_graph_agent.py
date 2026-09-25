from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult


class KnowledgeGraphAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="knowledge_graph_agent", description="Registers typed relations", capabilities=("knowledge_graph", "world_model"), risk_level="low"))

    async def run(self, task, context):
        graph = context.values["graph"]
        for relation in context.values.get("relations", []):
            graph.add_relation(relation)
        labels = [f"{item.relation.value}:{item.epistemic.value}" for item in graph.get_relations()]
        return AgentResult(success=True, confidence=0.3, summary="Relations registered. A relation is not a truth guarantee.", output={"agent": self.metadata.name, "relations": labels, "executed": False}, limitations=["CAUSES_HYPOTHESIS is not causal proof."])
