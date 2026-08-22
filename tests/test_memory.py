import asyncio

import pytest

from superagi.core.agents import BaseAgent
from superagi.core.models import AgentContext, AgentMetadata, AgentResult, Task
from superagi.memory import Document, MemoryRecord, MemoryType, SourceType, UniversalMemory
from superagi.memory.context import ContextBuilder
from superagi.memory.evidence import Evidence, EvidenceStatus, EvidenceStore, ProvenanceRecord, ProvenanceStage, ProvenanceStore
from superagi.memory.indexing import DocumentChunker, source_metadata
from superagi.memory.knowledge import Entity, EntityType, KnowledgeBase, Relation, RelationType
from superagi.memory.policies import PrivacyPolicy, RetentionPolicy
from superagi.memory.providers import InMemoryMemoryProvider
from superagi.memory.retrieval import RankingStrategy, Retriever
from superagi.memory.workflow import ResearchContextWorkflow


def run(coro):
    return asyncio.run(coro)


def test_memory_record_is_typed_and_duplicate_detection_is_source_aware():
    provider = InMemoryMemoryProvider()
    first = provider.store(MemoryRecord(content=" Solar power  output ", memory_type=MemoryType.RESEARCH, source="paper", source_id="p1"))
    duplicate = provider.store(MemoryRecord(content="solar power output", memory_type=MemoryType.RESEARCH, source="paper", source_id="p1"))
    different_source = provider.store(MemoryRecord(content="solar power output", memory_type=MemoryType.RESEARCH, source="paper", source_id="p2"))
    assert duplicate.id == first.id and different_source.id != first.id


def test_memory_filters_and_delete():
    provider = InMemoryMemoryProvider()
    provider.store(MemoryRecord(content="solar telemetry", memory_type=MemoryType.RESEARCH, source="paper", confidence=0.9))
    provider.store(MemoryRecord(content="solar telemetry", memory_type=MemoryType.WORKING, source="user", confidence=0.2))
    found = provider.search("solar", memory_type=MemoryType.RESEARCH, source="paper", min_confidence=0.8)
    assert len(found) == 1
    assert provider.delete(found[0].id) and provider.retrieve(found[0].id) is None


def test_document_and_chunking_with_overlap():
    document = Document(title="Power", content="one two three four five six", source="paper-1", source_type=SourceType.PAPER, authors=("A",))
    chunks = DocumentChunker(chunk_size=3, overlap=1).chunk(document)
    assert [chunk.position for chunk in chunks] == [0, 1, 2]
    assert chunks[0].content == "one two three" and "three" in chunks[1].content
    assert source_metadata(document, chunks[0])["source_type"] == "paper"


def test_ranking_and_retriever_metadata_filter():
    memory = InMemoryMemoryProvider()
    memory.store(MemoryRecord(content="orbital power telemetry", source="telemetry", confidence=0.9))
    retriever = Retriever(memory)
    document = Document(title="Orbit", content="orbital power telemetry", source="paper", source_type=SourceType.PAPER)
    retriever.add_document(document, DocumentChunker(20, 0).chunk(document))
    assert RankingStrategy().score("orbital power", document.content) == 1.0
    assert retriever.search("orbital", source="paper")
    assert all(result.metadata.get("source") == "paper" for result in retriever.search("orbital", source="paper") if "source" in result.metadata)


def test_knowledge_base_entities_relations():
    knowledge = KnowledgeBase()
    array = knowledge.add_entity(Entity(name="solar array", entity_type=EntityType.OBJECT))
    satellite = knowledge.add_entity(Entity(name="satellite", entity_type=EntityType.OBJECT))
    relation = knowledge.add_relation(Relation(source_entity_id=satellite.id, target_entity_id=array.id, relation_type=RelationType.USES, source="paper"))
    assert knowledge.get_entity(array.id) == array
    assert knowledge.get_relations(satellite.id) == [relation]
    assert knowledge.find_related(satellite.id) == [array]
    assert knowledge.search_entities("solar") == [array]


def test_evidence_and_provenance():
    evidence_store = EvidenceStore()
    evidence = evidence_store.add(Evidence(claim="irradiance affects output", source="paper", source_type="paper", excerpt="irradiance", confidence=0.9, status=EvidenceStatus.SUPPORTED))
    assert evidence_store.get(evidence.id) == evidence
    assert evidence_store.search("irradiance") == [evidence]
    assert evidence_store.link_to_claim("IRRADIANCE AFFECTS OUTPUT") == [evidence]
    provenance = ProvenanceStore()
    record = provenance.add(ProvenanceRecord(stage=ProvenanceStage.CHUNK, producer="chunker", source="paper", operation="chunk", output_references=(str(evidence.id),)))
    assert provenance.chain(str(evidence.id)) == [record]


def test_context_builder_enforces_maximum_context():
    memory = InMemoryMemoryProvider()
    memory.store(MemoryRecord(content="solar power output depends on irradiance", source="paper"))
    retriever = Retriever(memory)
    builder = ContextBuilder(retriever, max_context_size=10)
    task = Task(description="solar power")
    context = builder.build(task, AgentContext(task_id=task.id), "solar power")
    assert context.task_id == str(task.id)
    assert not context.relevant_memories and context.limitations == []


def test_universal_memory_document_context_and_forget():
    memory = UniversalMemory(max_context_size=1000)
    item = memory.remember("Satellite power uses solar arrays", memory_type=MemoryType.SEMANTIC, source="paper", source_id="paper-1", confidence=0.9)
    document = Document(title="Satellite", content="Solar arrays generate power for satellites.", source="paper-1", source_type=SourceType.PAPER)
    chunks = memory.ingest_document(document)
    task = Task(description="satellite power")
    context = run(memory.build_context(task, "satellite power"))
    assert memory.recall(item.id) == item
    assert chunks and context.relevant_memories and context.relevant_documents
    assert memory.forget(item.id)


def test_privacy_and_retention():
    record = MemoryRecord(content="ordinary finding")
    PrivacyPolicy().validate(record)
    with pytest.raises(ValueError):
        PrivacyPolicy().validate(MemoryRecord(content="api_key: do-not-store"))
    policy = RetentionPolicy(minimum_days=1)
    assert not policy.can_delete(record)


class ContextAgent(BaseAgent):
    async def run(self, task, context):
        assert "research_context" in context.values
        return AgentResult(success=True, summary="Answer grounded in supplied context", confidence=0.8)


def test_research_context_workflow_integrates_arc01():
    memory = UniversalMemory()
    memory.remember("Irradiance and orientation affect satellite power output", memory_type=MemoryType.RESEARCH, source="paper", source_id="p1", confidence=0.9)
    task = Task(description="What variables predict satellite power output?")
    agent = ContextAgent(AgentMetadata(name="context-agent"))
    result = run(ResearchContextWorkflow(memory).run(task, agent))
    assert result.success
    assert memory.search("satellite power")
