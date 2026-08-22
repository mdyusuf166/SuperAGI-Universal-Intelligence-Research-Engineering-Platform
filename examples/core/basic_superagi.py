from __future__ import annotations

import asyncio
import time

from superagi.core.agents import BaseAgent
from superagi.core.events import EventBus
from superagi.core.memory import InMemoryMemoryProvider
from superagi.core.models import AgentContext, AgentMetadata, AgentResult
from superagi.core.safety import AuditLogger
from superagi.core.tasks import TaskManager
from superagi.core.tools import CalculatorTool, TextAnalysisTool, ToolRegistry
from superagi.core.tracing import ExecutionTrace
from superagi.core.workflow import BasicAgentWorkflow


class ResearchAnalysisAgent(BaseAgent):
    async def run(self, task, context: AgentContext) -> AgentResult:
        return AgentResult(
            success=True,
            summary="Satellite power output depends on illumination, orientation, degradation, and load.",
            confidence=0.72,
            output={
                "tool_calls": [
                    ("calculator", {"expression": "0.85 * 100"}),
                    ("text_analysis", {"text": task.description}),
                ]
            },
        )


async def main() -> None:
    started = time.perf_counter()
    event_bus = EventBus()
    task_manager = TaskManager(event_bus)
    tools = ToolRegistry()
    tools.register(CalculatorTool())
    tools.register(TextAnalysisTool())
    agent = ResearchAnalysisAgent(AgentMetadata(name="research_analysis", description="Concise scientific analysis"))
    task = task_manager.create_task("Analyze the problem of predicting satellite power output.")
    workflow = BasicAgentWorkflow(agent, tools, task_manager=task_manager, event_bus=event_bus, memory=InMemoryMemoryProvider(), audit_logger=AuditLogger())
    result = await workflow.run(task)
    trace = ExecutionTrace(event_bus)
    print(f"Task ID: {task.id}")
    print(f"Plan ID: {workflow.last_plan.id}")
    print(f"Agent: {agent.metadata.name}")
    print("Tools: calculator, text_analysis")
    print(f"Steps: {', '.join(trace.event_types_for_task(task.id))}")
    print(f"Verification: {result.output['verification']['verification_status']}")
    print(f"Result: {result.summary}")
    print(f"Duration: {(time.perf_counter() - started) * 1000:.2f} ms")


if __name__ == "__main__":
    asyncio.run(main())
