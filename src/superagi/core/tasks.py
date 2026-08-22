from __future__ import annotations

from typing import Any
from uuid import UUID

from .events import EventBus
from .models import AgentResult, Event, EventType, Task, TaskStatus, utc_now


class TaskManager:
    _transitions = {
        TaskStatus.CREATED: {TaskStatus.QUEUED, TaskStatus.CANCELLED},
        TaskStatus.QUEUED: {TaskStatus.RUNNING, TaskStatus.CANCELLED},
        TaskStatus.RUNNING: {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED},
        TaskStatus.COMPLETED: set(), TaskStatus.FAILED: set(), TaskStatus.CANCELLED: set(),
    }

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self.events = event_bus or EventBus()
        self._tasks: dict[UUID, Task] = {}

    def create_task(self, description: str, **metadata: Any) -> Task:
        task = Task(description=description, metadata=metadata)
        self._tasks[task.id] = task
        self._emit(task, EventType.TASK_CREATED)
        return task

    def get_task(self, task_id: UUID) -> Task:
        try:
            return self._tasks[task_id]
        except KeyError as exc:
            raise KeyError(f"Unknown task: {task_id}") from exc

    def update_task(self, task_id: UUID, status: TaskStatus, *, result: AgentResult | None = None, error: str | None = None) -> Task:
        task = self.get_task(task_id)
        if status not in self._transitions[task.status]:
            raise ValueError(f"Invalid task transition: {task.status} -> {status}")
        task.status = status
        task.updated_at = utc_now()
        task.result = result
        task.error = error
        event_type = {
            TaskStatus.QUEUED: EventType.TASK_QUEUED,
            TaskStatus.RUNNING: EventType.TASK_STARTED,
            TaskStatus.COMPLETED: EventType.TASK_COMPLETED,
            TaskStatus.FAILED: EventType.TASK_FAILED,
            TaskStatus.CANCELLED: EventType.TASK_CANCELLED,
        }[status]
        self._emit(task, event_type, error=error or "")
        return task

    def cancel_task(self, task_id: UUID) -> Task:
        return self.update_task(task_id, TaskStatus.CANCELLED)

    def list_tasks(self, status: TaskStatus | None = None) -> list[Task]:
        tasks = list(self._tasks.values())
        return [task for task in tasks if status is None or task.status == status]

    def _emit(self, task: Task, event_type: EventType, **metadata: Any) -> None:
        self.events.publish(Event(event_type=event_type, task_id=task.id, metadata=metadata))
