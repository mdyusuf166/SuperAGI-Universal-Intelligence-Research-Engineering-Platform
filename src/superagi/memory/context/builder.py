from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ...core.models import AgentContext, Task
from ..evidence.evidence import Evidence
from ..knowledge.entities import Entity
from ..knowledge.relations import Relation
from ..models import Document, DocumentChunk, MemoryRecord
from ..retrieval.retriever import RetrievalResult, Retriever


class ResearchContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    task_id: str
    query: str
    relevant_memories: list[MemoryRecord] = Field(default_factory=list)
    relevant_documents: list[Document] = Field(default_factory=list)
    relevant_chunks: list[DocumentChunk] = Field(default_factory=list)
    relevant_entities: list[Entity] = Field(default_factory=list)
    relevant_relations: list[Relation] = Field(default_factory=list)
    relevant_evidence: list[Evidence] = Field(default_factory=list)
    source_references: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ContextBuilder:
    def __init__(self, retriever: Retriever, *, max_context_size: int = 6000) -> None:
        self.retriever = retriever
        self.max_context_size = max_context_size

    def build(self, task: Task, agent_context: AgentContext, query: str, *, entities: list[Entity] | None = None, relations: list[Relation] | None = None, evidence: list[Evidence] | None = None) -> ResearchContext:
        results = self.retriever.search(query, limit=100)
        memories = [result.item for result in results if isinstance(result.item, MemoryRecord)]
        documents = [result.item for result in results if isinstance(result.item, Document)]
        chunks = [result.item for result in results if isinstance(result.item, DocumentChunk)]
        used = 0
        selected_memories: list[MemoryRecord] = []
        selected_documents: list[Document] = []
        selected_chunks: list[DocumentChunk] = []
        for collection, selected in ((memories, selected_memories), (documents, selected_documents), (chunks, selected_chunks)):
            for item in collection:
                size = len(getattr(item, "content", ""))
                if used + size > self.max_context_size:
                    continue
                selected.append(item)
                used += size
        refs = [item.source for item in selected_memories + selected_documents]
        refs.extend(str(item.document_id) for item in selected_chunks)
        limitations = [] if results else ["No lexical matches were found; semantic retrieval is not enabled."]
        return ResearchContext(task_id=str(task.id), query=query, relevant_memories=selected_memories, relevant_documents=selected_documents, relevant_chunks=selected_chunks, relevant_entities=entities or [], relevant_relations=relations or [], relevant_evidence=evidence or [], source_references=refs, limitations=limitations)
