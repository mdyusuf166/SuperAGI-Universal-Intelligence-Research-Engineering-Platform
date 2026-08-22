from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from ..models import Document, DocumentChunk, MemoryRecord, MemoryType, SourceType
from ..providers.base import MemoryProvider
from .ranking import RankingStrategy


@dataclass(frozen=True)
class RetrievalResult:
    item: MemoryRecord | Document | DocumentChunk
    score: float
    metadata: dict[str, Any]


class Retriever:
    def __init__(self, provider: MemoryProvider, ranking: RankingStrategy | None = None) -> None:
        self.provider = provider
        self.ranking = ranking or RankingStrategy()
        self.documents: dict[UUID, Document] = {}
        self.chunks: dict[UUID, DocumentChunk] = {}

    def add_document(self, document: Document, chunks: list[DocumentChunk]) -> None:
        self.documents[document.id] = document
        self.chunks.update({chunk.id: chunk for chunk in chunks})

    def search(self, query: str, *, source: str | None = None, source_type: SourceType | None = None, memory_type: MemoryType | None = None, min_confidence: float | None = None, limit: int = 10) -> list[RetrievalResult]:
        results = [RetrievalResult(record, self.ranking.score(query, record.content), {"source": record.source}) for record in self.provider.search(query, memory_type=memory_type, source=source, min_confidence=min_confidence)]
        for document in self.documents.values():
            if source and document.source != source or source_type and document.source_type is not source_type:
                continue
            score = self.ranking.score(query, f"{document.title} {document.content}")
            if score:
                results.append(RetrievalResult(document, score, {"source": document.source, "source_type": document.source_type.value}))
        for chunk in self.chunks.values():
            score = self.ranking.score(query, chunk.content)
            if score:
                results.append(RetrievalResult(chunk, score, {"document_id": str(chunk.document_id), "position": chunk.position}))
        return sorted(results, key=lambda result: (-result.score, str(result.item.id)))[:limit]

    def retrieve_by_id(self, item_id: UUID) -> RetrievalResult | None:
        item = self.provider.retrieve(item_id) or self.documents.get(item_id) or self.chunks.get(item_id)
        return RetrievalResult(item, 1.0, {}) if item else None

    def retrieve_related(self, item_id: UUID, limit: int = 10) -> list[RetrievalResult]:
        item = self.retrieve_by_id(item_id)
        if item is None:
            return []
        if isinstance(item.item, Document):
            return [RetrievalResult(chunk, 1.0, {"document_id": str(item.item.id)}) for chunk in self.chunks.values() if chunk.document_id == item.item.id][:limit]
        return []
