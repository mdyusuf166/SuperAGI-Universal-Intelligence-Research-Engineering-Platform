from __future__ import annotations
from superagi.core.models import AgentContext, AgentResult, Task
from superagi.research.agents._base import ResearchAgent, metadata
from ..drug_discovery import CandidateScreening, CandidateRanking, DrugCandidate
class DrugDiscoveryAgent(ResearchAgent):
    def __init__(self): super().__init__(metadata("drug_discovery", "Computational candidate prioritization agent", ("screening", "ranking"))); self.screening = CandidateScreening(); self.ranking = CandidateRanking()
    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        candidates = [DrugCandidate(**item) if isinstance(item, dict) else item for item in context.values.get("candidates", [])]
        criteria = context.values.get("criteria", {}); ranked = self.ranking.rank(candidates, criteria)
        return AgentResult(success=True, output={"classification": "PROPOSED CANDIDATE", "ranking": ranked, "limitations": ["Not an approved drug, clinically effective, or safe for humans."]}, summary="Candidates computationally ranked.")
