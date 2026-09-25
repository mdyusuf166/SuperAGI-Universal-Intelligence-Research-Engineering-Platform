from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..evolution_cycle import EvolutionCycle


class EvolutionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="evolution_agent", description="Proposal-only capability-gap reports", capabilities=("evolution",), risk_level="low"))

    async def run(self, task, context):
        proposal = EvolutionCycle().propose(context.values["gap"], approved=bool(context.values.get("approved", False)), source=context.values.get("source"))
        return AgentResult(success=proposal.applied is False, confidence=0.2, summary="Evolution proposal. Not applied.", output={"agent": self.metadata.name, "lifecycle": proposal.lifecycle.value, "applied": proposal.applied, "change": proposal.change.kind}, limitations=proposal.limitations)
