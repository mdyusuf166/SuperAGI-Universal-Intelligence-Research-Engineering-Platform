from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from superagi.core.models import AgentContext, AgentResult, Task
from superagi.memory import Document, SourceType

from ._base import ResearchAgent, metadata


class LiteratureProvider(ABC):
    @abstractmethod
    def search(self, query: str) -> list[dict[str, Any]]:
        """Return source metadata from an explicit literature corpus."""

    @abstractmethod
    def get_document(self, identifier: str) -> Document | None:
        """Retrieve one known document."""


class MockLiteratureProvider(LiteratureProvider):
    def __init__(self, documents: list[Document] | None = None) -> None:
        self.documents = documents or [
            Document(title="Solar power variables", content="Solar panel output depends on irradiance, panel orientation, temperature, and system losses.", source="controlled-paper-1", source_type=SourceType.PAPER, authors=("Controlled Corpus",), metadata={"year": 2024, "identifier": "controlled-1"}),
            Document(title="Satellite power systems", content="Satellite power systems use solar arrays and energy storage to maintain electrical power during orbital operation.", source="controlled-paper-2", source_type=SourceType.PAPER, authors=("Controlled Corpus",), metadata={"year": 2024, "identifier": "controlled-2"}),
            Document(title="Predictive power modeling", content="A predictive model can use historical telemetry and environmental variables to estimate future power output.", source="controlled-paper-3", source_type=SourceType.PAPER, authors=("Controlled Corpus",), metadata={"year": 2024, "identifier": "controlled-3"}),
        ]

    def search(self, query: str) -> list[dict[str, Any]]:
        terms = set(query.casefold().split())
        results = []
        for document in self.documents:
            score = len(terms & set(f"{document.title} {document.content}".casefold().split()))
            if score:
                results.append({"title": document.title, "authors": list(document.authors), "year": document.metadata.get("year"), "source": document.source, "identifier": document.metadata.get("identifier", str(document.id)), "abstract": document.content, "metadata": {"lexical_score": score}})
        return sorted(results, key=lambda item: (-item["metadata"]["lexical_score"], item["identifier"]))

    def get_document(self, identifier: str) -> Document | None:
        return next((document for document in self.documents if identifier in {document.source, document.metadata.get("identifier"), str(document.id)}), None)


class LiteratureAgent(ResearchAgent):
    def __init__(self, provider: LiteratureProvider | None = None) -> None:
        super().__init__(metadata("literature_agent", "Searches a controlled literature corpus", ("literature_search", "source_metadata")))
        self.provider = provider or MockLiteratureProvider()

    def search(self, query: str) -> list[dict[str, Any]]:
        return self.provider.search(query)

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        results = self.search(task.description)
        return AgentResult(success=True, confidence=0.8 if results else 0.2, summary=f"Found {len(results)} controlled literature sources", output={"documents": results})
