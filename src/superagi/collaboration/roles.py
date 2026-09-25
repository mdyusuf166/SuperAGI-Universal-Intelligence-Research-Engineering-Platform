"""Role assignment. An automated participant cannot become the decision maker."""

from __future__ import annotations

from .models import Role


class RoleAssigner:
    def assign(self, participant: str, name: str, responsibilities: list[str] | None = None, *, human: bool = False) -> Role:
        if not human and name.casefold() in {"decision maker", "decision_maker"}:
            raise PermissionError("The system cannot take the decision-maker role")
        return Role(name=name, participant=participant, responsibilities=list(responsibilities or []), human_decision_maker=human and name.casefold() in {"decision maker", "decision_maker", "lead"})
