from __future__ import annotations

from superagi.core.events import EventBus
from superagi.core.models import Event, EventType

from .evidence.provenance import ProvenanceRecord, ProvenanceStage
from .models import MemoryType


class ResearchContextWorkflow:
    def __init__(self, memory, event_bus: EventBus | None = None) -> None:
        self.memory = memory
        self.events = event_bus or EventBus()

    async def run(self, task, agent):
        from superagi.core.models import AgentContext
        context = AgentContext(task_id=task.id)
        research_context = await self.memory.build_context(task, task.description, context)
        self.events.publish(Event(event_type=EventType.MEMORY_RETRIEVED, task_id=task.id, metadata={"result_count": len(research_context.relevant_memories) + len(research_context.relevant_documents)}))
        context.values["research_context"] = research_context.model_dump()
        self.events.publish(Event(event_type=EventType.AGENT_STARTED, task_id=task.id, agent_id=agent.id))
        result = await agent.run(task, context)
        self.events.publish(Event(event_type=EventType.AGENT_COMPLETED, task_id=task.id, agent_id=agent.id))
        stored = self.memory.remember(result.summary or str(result.output), memory_type=MemoryType.RESEARCH, source="agent", source_id=str(task.id), confidence=result.confidence)
        self.memory.provenance.add(ProvenanceRecord(stage=ProvenanceStage.AGENT_RESULT, producer=agent.metadata.name, source="agent", operation="research_answer", input_references=tuple(research_context.source_references), output_references=(str(stored.id),)))
        self.events.publish(Event(event_type=EventType.MEMORY_STORED, task_id=task.id, metadata={"memory_id": str(stored.id)}))
        return result
