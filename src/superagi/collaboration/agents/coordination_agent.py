from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..coordination import CoordinationService
from ..models import Claim


class CoordinationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="coordination_agent", description="Discovers ARC-09 capabilities and reports conflicts", capabilities=("coordination", "collaboration"), risk_level="low"))

    async def run(self, task, context):
        service = CoordinationService()
        result = service.coordinate(context.values["objective"], context.values.get("registry"), list(context.values.get("capabilities", [])))
        claims = [claim if isinstance(claim, Claim) else Claim(**claim) for claim in context.values.get("claims", [])]
        conflicts = service.claim_conflicts(claims)
        result["claim_conflicts"] = [item.model_dump() for item in conflicts]
        result["selected_conflict_winner"] = None
        return AgentResult(success=True, confidence=0.3, summary="Coordination result with conflicts left visible.", output={"agent": self.metadata.name, **result}, limitations=["No conflicting result was silently selected."])
