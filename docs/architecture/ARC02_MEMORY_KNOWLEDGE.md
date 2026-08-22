# ARC-02 Universal Memory and Knowledge Intelligence

SuperAGI is an experimental modular AGI research and scientific intelligence
platform. ARC-02 adds a provider-independent memory and knowledge layer while
leaving ARC-01 execution contracts intact.

## Memory Architecture

`UniversalMemory` composes a `MemoryProvider`, lexical `Retriever`, document
chunker, `KnowledgeBase`, `EvidenceStore`, provenance store, and privacy and
retention policies. The default provider is in-memory only. No vector database
or external service is required.

`MemoryType` supports working, episodic, semantic, procedural, research, and
experimental records. Records retain source, source ID, confidence, importance,
tags, timestamps, and metadata.

## Documents And Chunking

Documents require source and `SourceType` metadata. `DocumentChunker` splits
content into configurable word-sized chunks with configurable overlap and a
deterministic token estimate. No embeddings are created.

## Retrieval And Ranking

`Retriever` searches memory records, documents, and chunks with transparent
token-overlap scoring. It supports source, source type, memory type, confidence,
ID, and result-limit filtering. This is explicitly lexical retrieval, not
semantic or vector search.

## Knowledge Graph

`KnowledgeBase` stores typed entities and relations. Relations require both
endpoint entities and a declared source. The graph has generic relation types
such as `USES`, `CAUSES`, `PART_OF`, `STUDIES`, and `RELATED_TO`; it does not
hardcode medical or scientific claims.

## Evidence And Provenance

Evidence records contain claims, excerpts, source metadata, confidence, and an
explicit status. `EvidenceStore` supports search and claim linking.

`ProvenanceStore` records producer, operation, inputs, outputs, and stage. The
implemented chain is:

`SOURCE -> DOCUMENT -> CHUNK -> CLAIM/EVIDENCE -> AGENT_RESULT`

Results can therefore carry source references and limitations without
fabricating citations.

## Context Building And Agent Integration

`ContextBuilder` combines ARC-01 `Task` and `AgentContext` with relevant
memories, documents, chunks, entities, relations, evidence, source references,
and limitations. A configurable character budget prevents unbounded context.

`ResearchContextWorkflow` places the resulting context in the existing
`AgentContext.values["research_context"]`, invokes an ARC-01-compatible agent,
stores the result as research memory, records provenance, and emits memory and
agent events.

## Privacy And Retention

`PrivacyPolicy` rejects credential-like content including API keys, passwords,
tokens, credentials, and secrets. `RetentionPolicy` provides minimum retention
metadata and deletion checks. Secret values are never logged or stored.

## Extension Points

Abstract boundaries exist for vector, graph, PostgreSQL, and Redis memory
providers, plus embedding, reranking, web, and paper retrieval. These are
interfaces only. Future implementations can be added without changing agent
contracts or the current in-memory behavior.

## Demonstrations

- `examples/memory/universal_memory_demo.py` demonstrates document ingestion,
  chunks, memory, entities, relations, evidence, context, an agent result, and
  provenance.
- `examples/research/research_context_demo.py` demonstrates a bounded,
  evidence-aware research answer with explicit lexical-retrieval limitations.
