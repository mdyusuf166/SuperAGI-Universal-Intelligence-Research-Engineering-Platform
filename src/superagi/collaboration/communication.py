"""Summaries built only from supplied artifacts."""

from __future__ import annotations


class CommunicationSupport:
    def summarize(self, *, meetings=None, tasks=None, project=None, research=None, engineering=None, decisions=None, participants=None, evidence=None, sources=None) -> dict:
        def render(name, value):
            if value is None or value == [] or value == "":
                return f"{name}: not provided"
            if isinstance(value, list):
                return f"{name}: " + "; ".join(str(item) for item in value)
            return f"{name}: {value}"

        action_items = [task.title if hasattr(task, "title") else str(task) for task in (tasks or [])]
        return {
            "meeting_summary": render("meetings", meetings),
            "task_summary": render("tasks", action_items),
            "project_update": render("project", project),
            "research_summary": render("research", research),
            "engineering_summary": render("engineering", engineering),
            "decisions": render("decisions", decisions),
            "participants": render("participants", participants),
            "evidence": render("evidence", evidence),
            "action_items": action_items,
            "sources": list(sources or []),
            "fabricated": False,
        }
