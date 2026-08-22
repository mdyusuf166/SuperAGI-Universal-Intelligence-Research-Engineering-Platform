from __future__ import annotations

import asyncio

from superagi.core.models import AgentContext, AgentMetadata, AgentResult, Task
from superagi.memory import Document, SourceType, UniversalMemory
from superagi.memory.workflow import ResearchContextWorkflow


class ResearchAgent:
    metadata = AgentMetadata(name="research_context_agent", description="Produces concise evidence-aware answers")

    @property
    def id(self):
        return self.metadata.id

    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        research = context.values["research_context"]
        sources = research["source_references"]
        limitations = research["limitations"] or ["Lexical retrieval only; no web or semantic retrieval was used."]
        return AgentResult(success=True, confidence=0.82, summary="Consider irradiance, orientation, temperature, system losses, historical telemetry, and environmental variables.", limitations=limitations, output={"source_references": sources})


async def main() -> None:
    memory = UniversalMemory()
    memory.ingest_document(Document(title="Controlled satellite study", content="Irradiance, orientation, temperature, losses, telemetry, and environmental variables affect satellite power output.", source="controlled-study-1", source_type=SourceType.EXPERIMENT))
    task = Task(description="What variables should be considered when predicting satellite power output?")
    agent = ResearchAgent()
    result = await ResearchContextWorkflow(memory).run(task, agent)
    context = await memory.build_context(task, task.description)
    print(f"Question: {task.description}")
    print(f"Retrieved information: {len(context.relevant_documents)} documents, {len(context.relevant_chunks)} chunks")
    print(f"Answer: {result.summary}")
    print(f"Limitations: {result.limitations}")
    print(f"Source references: {result.output['source_references']}")


if __name__ == "__main__":
    asyncio.run(main())
