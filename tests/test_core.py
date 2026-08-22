import asyncio
from pathlib import Path

import pytest

from superagi.core.agents import AgentRegistry, BaseAgent
from superagi.core.events import EventBus
from superagi.core.memory import InMemoryMemoryProvider, MemoryType
from superagi.core.models import AgentContext, AgentMetadata, AgentResult, EventType, Plan, PlanStep, TaskStatus
from superagi.core.planning import PlanExecutor
from superagi.core.providers import MockModelProvider
from superagi.core.reasoning import ReasoningEngine
from superagi.core.safety import AuditLogger, PermissionManager
from superagi.core.tasks import TaskManager
from superagi.core.tools import CalculatorTool, PermissionLevel, SandboxFileReadTool, TextAnalysisTool, ToolRegistry
from superagi.core.tracing import ExecutionTrace
from superagi.core.workflow import BasicAgentWorkflow


class DemoAgent(BaseAgent):
    async def run(self, task, context):
        return AgentResult(success=True, summary=f"Analyzed {task.description}", output={"tool_calls": [("calculator", {"expression": "2 + 2"}), ("text_analysis", {"text": task.description})]})


def run(coro):
    return asyncio.run(coro)


def test_task_lifecycle_and_events():
    bus = EventBus()
    manager = TaskManager(bus)
    task = manager.create_task("test task")
    manager.update_task(task.id, TaskStatus.QUEUED)
    manager.update_task(task.id, TaskStatus.RUNNING)
    manager.update_task(task.id, TaskStatus.COMPLETED)
    assert [event.event_type for event in bus.events(task.id)] == [EventType.TASK_CREATED, EventType.TASK_QUEUED, EventType.TASK_STARTED, EventType.TASK_COMPLETED]


def test_task_cancel_and_invalid_transition():
    manager = TaskManager()
    task = manager.create_task("cancel me")
    manager.cancel_task(task.id)
    assert task.status is TaskStatus.CANCELLED
    with pytest.raises(ValueError):
        manager.update_task(task.id, TaskStatus.RUNNING)


def test_agent_registry_duplicate():
    registry = AgentRegistry()
    agent = DemoAgent(AgentMetadata(name="demo"))
    registry.register(agent)
    assert registry.exists("demo") and registry.get("demo") is agent
    with pytest.raises(ValueError):
        registry.register(agent)


def test_tools_and_sandbox(tmp_path: Path):
    assert run(CalculatorTool().execute(expression="2 * (3 + 4)" )).output["value"] == 14
    assert run(TextAnalysisTool().execute(text="one two")).output["words"] == 2
    file = tmp_path / "note.txt"
    file.write_text("hello", encoding="utf-8")
    tool = SandboxFileReadTool(tmp_path)
    assert run(tool.execute(path="note.txt")).output["content"] == "hello"
    assert not run(tool.execute(path="../note.txt")).success


def test_tool_registry_duplicate():
    registry = ToolRegistry()
    tool = CalculatorTool()
    registry.register(tool)
    with pytest.raises(ValueError):
        registry.register(tool)


def test_plan_executor_dependencies_parallel_and_retry():
    calls = []
    attempts = {"a": 0}

    async def handler(step):
        calls.append(step.step_id)
        if step.step_id == "a" and attempts["a"] == 0:
            attempts["a"] += 1
            raise RuntimeError("retry")
        return step.step_id

    plan = Plan(task_id=TaskManager().create_task("plan").id, steps=[PlanStep(step_id="a", description="a", max_retries=1), PlanStep(step_id="b", description="b", dependencies=("a",))])
    run(PlanExecutor().execute(plan, handler))
    assert calls == ["a", "a", "b"] and plan.steps[0].retry_count == 1


def test_plan_executor_timeout_and_cancellation():
    async def slow(_):
        await asyncio.sleep(0.05)

    plan = Plan(task_id=TaskManager().create_task("timeout").id, steps=[PlanStep(step_id="slow", description="slow", timeout=0.001)])
    with pytest.raises(TimeoutError):
        run(PlanExecutor().execute(plan, slow))
    assert plan.steps[0].status.value == "timeout"


def test_memory_and_provider():
    memory = InMemoryMemoryProvider()
    item_id = memory.store("satellite power", MemoryType.SEMANTIC)
    assert memory.retrieve(item_id)["value"] == "satellite power"
    assert memory.search("SATELLITE", MemoryType.SEMANTIC)
    assert memory.delete(item_id)
    assert run(MockModelProvider().generate("hello")).startswith("Mock response")


def test_reasoning_is_structured_and_concise():
    engine = ReasoningEngine()
    report = engine.analyze_problem("power")
    verified = engine.verify_result(report, ["measured evidence"])
    assert verified.verification_status == "verified"
    assert engine.generate_hypotheses("power")


def test_permission_and_audit_redaction():
    permissions = PermissionManager()
    request = permissions.authorize("danger", "high_risk")
    assert request is not None
    permissions.approve(request)
    assert permissions.authorize("danger", "high_risk") is None
    audit = AuditLogger()
    audit.log("test", token="secret", task_id="1")
    assert audit.records[0]["token"] == "[REDACTED]"


def test_tool_contract_exposes_schema_and_risk_enum():
    tool = CalculatorTool()
    assert tool.input_schema == {} and tool.output_schema == {}
    assert tool.risk_level is PermissionLevel.READ_ONLY


def test_workflow_emits_trace_and_stores_memory():
    bus = EventBus()
    tasks = TaskManager(bus)
    agent = DemoAgent(AgentMetadata(name="demo"))
    tools = ToolRegistry()
    tools.register(CalculatorTool())
    tools.register(TextAnalysisTool())
    task = tasks.create_task("predict satellite power output")
    result = run(BasicAgentWorkflow(agent, tools, task_manager=tasks, event_bus=bus).run(task))
    trace = ExecutionTrace(bus)
    event_types = trace.event_types_for_task(task.id)
    assert result.success and task.status is TaskStatus.COMPLETED
    assert EventType.TOOL_COMPLETED.value in event_types
    assert event_types[-1] == EventType.TASK_COMPLETED.value
