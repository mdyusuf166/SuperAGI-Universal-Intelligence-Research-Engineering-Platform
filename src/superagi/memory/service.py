from __future__ import annotations

from typing import Any
from uuid import UUID

from .context.builder import ContextBuilder, ResearchContext
from .evidence.evidence import Evidence, EvidenceStore
from .evidence.provenance import ProvenanceRecord, ProvenanceStage, ProvenanceStore
from .indexing.chunker import DocumentChunker
from .indexing.metadata import source_metadata
from .knowledge.knowledge_base import KnowledgeBase
from .models import Document, DocumentChunk, MemoryRecord, MemoryType, SourceType
from .policies.privacy import PrivacyPolicy
from .policies.retention import RetentionPolicy
from .providers.base import MemoryProvider
from .providers.in_memory import InMemoryMemoryProvider
from .retrieval.retriever import RetrievalResult, Retriever


class UniversalMemory:
    def __init__(self, provider: MemoryProvider | None = None, *, max_context_size: int = 6000) -> None:
        self.provider = provider or InMemoryMemoryProvider()
        self.chunker = DocumentChunker()
        self.retriever = Retriever(self.provider)
        self.knowledge = KnowledgeBase()
        self.evidence = EvidenceStore()
        self.provenance = ProvenanceStore()
        self.retention = RetentionPolicy()
        self.privacy = PrivacyPolicy()
        self.context_builder = ContextBuilder(self.retriever, max_context_size=max_context_size)

    def remember(self, content: str, *, memory_type: MemoryType = MemoryType.WORKING, source: str = "system", source_id: str | None = None, importance: float = 0.5, confidence: float = 0.5, tags: tuple[str, ...] = (), metadata: dict[str, Any] | None = None) -> MemoryRecord:
        record = MemoryRecord(content=content, memory_type=memory_type, source=source, source_id=source_id, importance=importance, confidence=confidence, tags=tags, metadata=metadata or {})
        self.privacy.validate(record)
        stored = self.provider.store(record)
        self.provenance.add(ProvenanceRecord(stage=ProvenanceStage.SOURCE, producer="UniversalMemory", source=source, operation="remember", output_references=(str(stored.id),)))
        return stored

    def recall(self, memory_id: UUID) -> MemoryRecord | None:
        return self.provider.retrieve(memory_id)

    def search(self, query: str, **filters: Any) -> list[RetrievalResult]:
        return self.retriever.search(query, **filters)

    def forget(self, memory_id: UUID) -> bool:
        record = self.provider.retrieve(memory_id)
        if record is not None and not self.retention.can_delete(record):
            raise PermissionError("Retention policy prevents deletion")
        return self.provider.delete(memory_id)

    def related(self, item_id: UUID) -> list[RetrievalResult]:
        return self.retriever.retrieve_related(item_id)

    def ingest_document(self, document: Document) -> list[DocumentChunk]:
        chunks = self.chunker.chunk(document)
        self.retriever.add_document(document, chunks)
        self.provenance.add(ProvenanceRecord(stage=ProvenanceStage.DOCUMENT, producer="UniversalMemory", source=document.source, operation="ingest", input_references=(document.source,), output_references=(str(document.id),)))
        for chunk in chunks:
            self.provenance.add(ProvenanceRecord(stage=ProvenanceStage.CHUNK, producer="DocumentChunker", source=document.source, operation="chunk", input_references=(str(document.id),), output_references=(str(chunk.id),), metadata=source_metadata(document, chunk)))
        return chunks

    async def build_context(self, task, query: str, agent_context=None) -> ResearchContext:
        from superagi.core.models import AgentContext
        context = agent_context or AgentContext(task_id=task.id)
        evidence = self.evidence.search(query)
        entities = self.knowledge.search_entities(query)
        relation_map = {relation.id: relation for entity in entities for relation in self.knowledge.get_relations(entity.id)}
        relations = list(relation_map.values())
        return self.context_builder.build(task, context, query, entities=entities, relations=relations, evidence=evidence)

    def add_evidence(self, evidence: Evidence) -> Evidence:
        stored = self.evidence.add(evidence)
        self.provenance.add(ProvenanceRecord(stage=ProvenanceStage.EVIDENCE, producer="UniversalMemory", source=evidence.source, operation="record_evidence", input_references=(evidence.source_id or evidence.source,), output_references=(str(stored.id),)))
        return stored
