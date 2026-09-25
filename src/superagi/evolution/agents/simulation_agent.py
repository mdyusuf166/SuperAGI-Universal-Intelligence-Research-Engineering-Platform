from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..simulation import MockSimulationBackend


class SimulationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="simulation_agent", description="Deterministic mock simulation", capabilities=("simulation", "evolution"), risk_level="low"))

    async def run(self, task, context):
        result = MockSimulationBackend().run(context.values["scenario"])
        return AgentResult(success=result.status.value == "COMPLETED", confidence=0.3, summary="Mock simulation result.", output={"agent": self.metadata.name, "status": result.status.value, "classification": result.classification.value, "step_count": result.step_count}, limitations=result.limitations)
