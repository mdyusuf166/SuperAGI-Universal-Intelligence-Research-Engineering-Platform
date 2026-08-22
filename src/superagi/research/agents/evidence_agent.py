from __future__ import annotations

from superagi.core.models import AgentContext, AgentResult, Task
from superagi.memory import Document
from superagi.memory.evidence import Evidence, EvidenceStatus

from ._base import ResearchAgent, metadata


class EvidenceExtractor:
    def extract(self, document: Document) -> list[Evidence]:
        return [Evidence(claim=sentence.strip(), source=document.source, source_type=document.source_type.value, source_id=str(document.id), excerpt=sentence.strip(), confidence=0.8, status=EvidenceStatus.SUPPORTED, metadata={"document_id": str(document.id)}) for sentence in document.content.split(".") if sentence.strip()]


class EvidenceAgent(ResearchAgent):
    def __init__(self, extractor: EvidenceExtractor | None = None) -> None:
        super().__init__(metadata("evidence_agent", "Extracts source-grounded evidence", ("evidence_extraction", "provenance")))
        self.extractor = extractor or EvidenceExtractor()

    def extract(self, document: Document) -> list[Evidence]:
        return self.extractor.extract(document)

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        documents = context.values.get("documents", [])
        evidence = [item for document in documents for item in self.extract(document)]
        return AgentResult(success=True, confidence=0.8 if evidence else 0.2, summary=f"Extracted {len(evidence)} evidence items", output={"evidence": [item.model_dump() for item in evidence]})
