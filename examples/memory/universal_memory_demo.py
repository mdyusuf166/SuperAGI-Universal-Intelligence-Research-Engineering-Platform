from __future__ import annotations

import asyncio

from superagi.core.models import AgentContext, AgentMetadata, AgentResult, Task
from superagi.memory import Document, SourceType, UniversalMemory
from superagi.memory.evidence import Evidence, EvidenceStatus
from superagi.memory.knowledge import Entity, EntityType, Relation, RelationType


class ContextAgent:
    metadata = AgentMetadata(name="memory_research_agent", description="Answers from supplied context")

    @property
    def id(self):
        return self.metadata.id

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        research = context.values["research_context"]
        sources = research["source_references"]
        return AgentResult(success=True, confidence=0.86, summary="Use irradiance, orientation, temperature, losses, telemetry, and environmental variables to predict satellite power output.", output={"source_references": sources})


async def main() -> None:
    memory = UniversalMemory(max_context_size=2000)
    corpus = [
        "Solar panel output depends on irradiance, panel orientation, temperature, and system losses.",
        "Satellite power systems use solar arrays and energy storage to maintain electrical power during orbital operation.",
        "A predictive model can use historical telemetry and environmental variables to estimate future power output.",
    ]
    documents = [Document(title=f"Controlled research document {index}", content=text, source=f"controlled-{index}", source_type=SourceType.PAPER) for index, text in enumerate(corpus, 1)]
    for document in documents:
        memory.ingest_document(document)
        memory.remember(document.content, memory_type="research", source=document.source, source_id=str(document.id), confidence=0.9)
    satellite = memory.knowledge.add_entity(Entity(name="satellite", entity_type=EntityType.OBJECT))
    power = memory.knowledge.add_entity(Entity(name="power output", entity_type=EntityType.CONCEPT))
    memory.knowledge.add_relation(Relation(source_entity_id=satellite.id, target_entity_id=power.id, relation_type=RelationType.MEASURED_BY, source="controlled corpus", confidence=0.8))
    for document in documents:
        memory.add_evidence(Evidence(claim="variables influence satellite power prediction", source=document.source, source_type=document.source_type.value, source_id=str(document.id), excerpt=document.content, confidence=0.9, status=EvidenceStatus.SUPPORTED))
    task = Task(description="How can satellite power output be predicted?")
    context = await memory.build_context(task, task.description)
    agent = ContextAgent()
    result = await agent.run(task, AgentContext(task_id=task.id, values={"research_context": context.model_dump()}))
    print(f"Query: {task.description}")
    print(f"Retrieved memories: {len(context.relevant_memories)}")
    print(f"Retrieved evidence: {len(context.relevant_evidence)}")
    print(f"Entities: {[entity.name for entity in context.relevant_entities]}")
    print(f"Relations: {len(context.relevant_relations)}")
    print(f"Context: {len(context.relevant_documents)} documents, {len(context.relevant_chunks)} chunks")
    print(f"Final result: {result.summary}")
    print(f"Provenance chain: {len(memory.provenance.records)} records")


if __name__ == "__main__":
    asyncio.run(main())
