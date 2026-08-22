from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from .models import ExecutionStatus, Plan, PlanStep, Task


class Planner:
    def create_plan(self, task: Task) -> Plan:
        return Plan(task_id=task.id, steps=[PlanStep(step_id="analyze", description=f"Analyze: {task.description}")])


class PlanExecutor:
    async def execute(self, plan: Plan, handler: Callable[[PlanStep], Awaitable[Any]]) -> Plan:
        completed: set[str] = set()
        pending = {step.step_id: step for step in plan.steps}
        while pending:
            ready = [step for step in pending.values() if set(step.dependencies) <= completed]
            if not ready:
                raise ValueError("Plan contains unresolved or circular dependencies")
            results = await asyncio.gather(*(self._run_step(step, handler) for step in ready), return_exceptions=True)
            for step, result in zip(ready, results):
                pending.pop(step.step_id)
                if isinstance(result, Exception):
                    raise result
                completed.add(step.step_id)
        return plan

    async def _run_step(self, step: PlanStep, handler: Callable[[PlanStep], Awaitable[Any]]) -> Any:
        attempts = 0
        while True:
            step.status = ExecutionStatus.RUNNING
            try:
                operation = handler(step)
                if step.timeout is not None:
                    result = await asyncio.wait_for(operation, timeout=step.timeout)
                else:
                    result = await operation
                step.status = ExecutionStatus.COMPLETED
                return result
            except asyncio.TimeoutError:
                step.status = ExecutionStatus.TIMEOUT
                error: Exception = TimeoutError(f"Plan step timed out: {step.step_id}")
            except asyncio.CancelledError:
                step.status = ExecutionStatus.CANCELLED
                raise
            except Exception as exc:
                step.status = ExecutionStatus.FAILED
                error = exc
            if attempts >= step.max_retries:
                raise error
            attempts += 1
            step.retry_count = attempts
