from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .agents import BaseAgent
from .events import EventBus
from .memory import InMemoryMemoryProvider, MemoryProvider
from .models import AgentContext, AgentResult, Event, EventType, Task, ToolResult
from .planning import Planner
from .planning import PlanExecutor
from .reasoning import ReasoningEngine
from .safety import AuditLogger, PermissionManager
from .tasks import TaskManager
from .tools import BaseTool, ToolRegistry


class WorkflowStep(ABC):
    @abstractmethod
    async def run(self, task: Task, context: AgentContext) -> dict[str, Any]:
        """Run one workflow stage."""


class Workflow:
    def __init__(self, name: str, steps: list[WorkflowStep]) -> None:
        self.name = name
        self.steps = steps


class WorkflowRegistry:
    def __init__(self) -> None:
        self._workflows: dict[str, Workflow] = {}

    def register(self, workflow: Workflow) -> None:
        if workflow.name in self._workflows:
            raise ValueError(f"Workflow already registered: {workflow.name}")
        self._workflows[workflow.name] = workflow

    def get(self, name: str) -> Workflow:
        return self._workflows[name]


class BasicAgentWorkflow:
    def __init__(self, agent: BaseAgent, tools: ToolRegistry, *, task_manager: TaskManager | None = None, event_bus: EventBus | None = None, memory: MemoryProvider | None = None, permission_manager: PermissionManager | None = None, audit_logger: AuditLogger | None = None) -> None:
        self.events = event_bus or EventBus()
        self.tasks = task_manager or TaskManager(self.events)
        self.agent = agent
        self.tools = tools
        self.memory = memory or InMemoryMemoryProvider()
        self.permissions = permission_manager or PermissionManager()
        self.audit = audit_logger or AuditLogger()
        self.planner = Planner()
        self.plan_executor = PlanExecutor()
        self.reasoning = ReasoningEngine()
        self.last_plan = None

    async def run(self, task: Task) -> AgentResult:
        self.tasks.update_task(task.id, task.status.QUEUED)
        self.tasks.update_task(task.id, task.status.RUNNING)
        plan = self.planner.create_plan(task)
        self.last_plan = plan
        self._emit(EventType.PLAN_CREATED, task)
        self._emit(EventType.PLAN_STARTED, task)
        context = AgentContext(task_id=task.id)
        self._emit(EventType.AGENT_STARTED, task, agent_id=self.agent.id)
        self.agent.status = self.agent.status.RUNNING
        try:
            async def execute_plan_step(_step):
                return await self.agent.run(task, context)

            plan_result: dict[str, AgentResult] = {}

            async def capture_plan_result(step):
                plan_result[step.step_id] = await execute_plan_step(step)

            await self.plan_executor.execute(plan, capture_plan_result)
            agent_result = plan_result["analyze"]
            self.agent.status = self.agent.status.COMPLETED
            self._emit(EventType.AGENT_COMPLETED, task, agent_id=self.agent.id)
            for tool_name, arguments in agent_result.output.get("tool_calls", []):
                tool = self.tools.get(tool_name)
                approval = self.permissions.authorize(tool.name, tool.risk_level)
                if approval:
                    raise PermissionError(f"Approval required for tool: {tool.name}")
                self._emit(EventType.TOOL_STARTED, task, agent_id=self.agent.id, tool_id=tool.id)
                tool_result: ToolResult = await tool.execute(**arguments)
                if not tool_result.success:
                    raise RuntimeError(tool_result.error or "Tool failed")
                context.values[tool_name] = tool_result.output
                self._emit(EventType.TOOL_COMPLETED, task, agent_id=self.agent.id, tool_id=tool.id)
            self._emit(EventType.PLAN_COMPLETED, task)
            self._emit(EventType.VERIFICATION_STARTED, task, agent_id=self.agent.id)
            report = self.reasoning.analyze_problem(task.description)
            verified = self.reasoning.verify_result(report, [agent_result.summary])
            self._emit(EventType.VERIFICATION_COMPLETED, task, agent_id=self.agent.id, metadata={"status": verified.verification_status})
            self.memory.store(verified.model_dump(), metadata={"task_id": str(task.id)})
            result = agent_result.model_copy(update={"output": {**agent_result.output, "verification": verified.model_dump()}})
            self.tasks.update_task(task.id, task.status.COMPLETED, result=result)
            return result
        except Exception as exc:
            self.agent.status = self.agent.status.FAILED
            self._emit(EventType.AGENT_FAILED, task, agent_id=self.agent.id, error=str(exc))
            self._emit(EventType.PLAN_FAILED, task, error=str(exc))
            self.tasks.update_task(task.id, task.status.FAILED, error=str(exc))
            raise

    def _emit(self, event_type: EventType, task: Task, *, agent_id=None, tool_id=None, metadata=None, **extra: Any) -> None:
        self.events.publish(Event(event_type=event_type, task_id=task.id, agent_id=agent_id, tool_id=tool_id, metadata={**(metadata or {}), **extra}))
