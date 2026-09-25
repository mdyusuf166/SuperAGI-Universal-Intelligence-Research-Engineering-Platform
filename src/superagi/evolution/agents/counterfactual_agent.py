from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..counterfactual import CounterfactualEngine
from ..simulation import MockSimulationBackend


class CounterfactualAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="counterfactual_agent", description="Declared alternative trajectories, not causal identification", capabilities=("counterfactual", "evolution"), risk_level="low"))

    async def run(self, task, context):
        result = CounterfactualEngine(MockSimulationBackend()).compare(context.values["baseline"], context.values["alternative"])
        return AgentResult(success=True, confidence=0.2, summary="Counterfactual simulation. Not causally verified.", output={"agent": self.metadata.name, "label": result.label, "causal_status": result.causal_status, "verification": result.verification, "deltas": [item.delta for item in result.differences]}, limitations=result.limitations)
