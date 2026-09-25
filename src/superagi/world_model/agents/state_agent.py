from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult


class WorldStateAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="world_state_agent", description="Reads snapshot labels without promoting simulated state", capabilities=("world_state", "world_model"), risk_level="low"))

    async def run(self, task, context):
        timeline = context.values["timeline"]
        labels = [(item.epistemic.value, item.state.label) for item in timeline.snapshots()]
        return AgentResult(success=True, confidence=0.3, summary="Snapshot labels preserved.", output={"agent": self.metadata.name, "snapshots": labels, "executed": False}, limitations=["SIMULATED and PREDICTED snapshots are not observations."])
