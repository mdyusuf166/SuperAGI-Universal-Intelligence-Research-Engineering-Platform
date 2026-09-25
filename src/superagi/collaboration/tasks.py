"""Collaboration tasks linked to ARC-01 Task records."""

from __future__ import annotations

from uuid import UUID

from superagi.core.tasks import TaskManager

from .models import CollaborationTask


class TaskCoordinator:
    def __init__(self, manager: TaskManager | None = None) -> None:
        self.manager = manager or TaskManager()
        self.tasks: dict[UUID, CollaborationTask] = {}

    def create(self, title: str, owner: str, *, priority: int = 0, dependencies: tuple[UUID, ...] = (), evidence: tuple[str, ...] = (), blockers: tuple[str, ...] = (), completion_criteria: tuple[str, ...] = (), status: str = "PENDING") -> CollaborationTask:
        core = self.manager.create_task(title)
        task = CollaborationTask(title=title, owner=owner, core_task_id=core.id, priority=priority, dependencies=list(dependencies), evidence=list(evidence), blockers=list(blockers), completion_criteria=list(completion_criteria), status="BLOCKED" if blockers else status)
        self.tasks[task.id] = task
        return task

    def order(self, tasks: list[CollaborationTask] | None = None) -> dict:
        selected = list(self.tasks.values() if tasks is None else tasks)
        pending = {task.id: task for task in selected}
        ordered: list[CollaborationTask] = []
        while pending:
            ready = [task for task in pending.values() if all(dependency not in pending for dependency in task.dependencies)]
            if not ready:
                return {"ordered": ordered, "cycle": True, "blocked": [task.title for task in pending.values()]}
            ready.sort(key=lambda task: (-task.priority, task.title))
            for task in ready:
                ordered.append(task)
                pending.pop(task.id)
        return {"ordered": ordered, "cycle": False, "blocked": []}
