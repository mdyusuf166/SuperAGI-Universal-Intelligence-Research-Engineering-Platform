from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..world_model import WorldModel


class WorldModelAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="world_model_agent", description="Typed world model with optional ARC-02 storage", capabilities=("world_model", "evolution"), risk_level="low"))

    async def run(self, task, context):
        model = context.values.get("model") or WorldModel()
        stored = model.remember(context.values.get("memory"), context.values.get("source"))
        return AgentResult(success=True, confidence=0.3, summary=model.summary(), output={"agent": self.metadata.name, "summary": model.summary(), "stored": stored["stored"], "provenance_missing": model.provenance.missing if model.provenance else True}, limitations=["The world model records declared entities only."])
