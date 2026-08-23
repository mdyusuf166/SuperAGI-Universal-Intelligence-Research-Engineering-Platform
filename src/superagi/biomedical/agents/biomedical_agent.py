from __future__ import annotations
from superagi.core.models import AgentContext, AgentResult, Task
from superagi.memory import UniversalMemory
from superagi.research.models import ResearchQuestion
from ..models import BiomedicalResearchResult
from superagi.research.agents._base import ResearchAgent, metadata

class BiomedicalResearchAgent(ResearchAgent):
    def __init__(self, memory: UniversalMemory | None = None) -> None:
        super().__init__(metadata("biomedical_research", "Memory-grounded biomedical research coordinator", ("biomedical research", "evidence boundaries"))); self.memory = memory or UniversalMemory()
    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        question = context.values.get("research_question") or ResearchQuestion(question=task.description, domain="biomedical")
        if isinstance(question, dict): question = ResearchQuestion(**question)
        hits = self.memory.search(question.question)
        evidence = [{"content": hit.record.content, "source": hit.record.source, "classification": "EVIDENCE"} for hit in hits]
        result = BiomedicalResearchResult(question=question.question, findings=[], evidence=evidence, evidence_ids=[], knowledge_gaps=["No evidence is fabricated; retrieval may be empty."], limitations=["Not clinical advice or experimental validation."], provenance_ids=[])
        stored = self.memory.remember(str(result.model_dump()), source="biomedical_research_agent", source_id=str(question.id), metadata={"classification": "UNKNOWN"})
        result.provenance_ids = [str(stored.id)]
        return AgentResult(success=True, output=result.model_dump(), summary="Biomedical research context prepared.", limitations=result.limitations)
