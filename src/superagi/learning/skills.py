"""Deterministic skill dependency graph. The graph does not imply mastery."""

from __future__ import annotations

from .models import Skill, SkillPrerequisite, SkillStatus
from .safety import LearningSafetyPolicy


class SkillGraph:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._requires: dict[str, set[str]] = {}
        self.safety = LearningSafetyPolicy()

    def add_skill(self, skill: Skill) -> Skill:
        self.safety.guard(skill.name)
        key = skill.name.casefold()
        if key in self._skills:
            raise ValueError(f"Duplicate skill: {skill.name}")
        self._skills[key] = skill
        self._requires[key] = set()
        return skill

    def get_skill(self, name: str) -> Skill:
        try:
            return self._skills[name.casefold()]
        except KeyError as exc:
            raise KeyError(f"Unknown skill: {name}") from exc

    def add_prerequisite(self, prerequisite: SkillPrerequisite) -> None:
        skill = prerequisite.skill.casefold()
        required = prerequisite.required.casefold()
        if skill not in self._skills or required not in self._skills:
            raise ValueError("Invalid skill reference")
        if skill == required:
            raise ValueError("A skill cannot require itself")
        self._requires[skill].add(required)
        if self._has_cycle():
            self._requires[skill].discard(required)
            raise ValueError(f"Prerequisite cycle: {prerequisite.skill} -> {prerequisite.required}")

    def prerequisites(self, name: str) -> list[str]:
        key = self.get_skill(name).name.casefold()
        return sorted(self._skills[item].name for item in self._requires[key])

    def dependencies(self, name: str) -> list[str]:
        key = self.get_skill(name).name.casefold()
        seen: list[str] = []
        stack = sorted(self._requires[key], reverse=True)
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.append(current)
            stack.extend(sorted(self._requires[current] - set(seen), reverse=True))
        return [self._skills[item].name for item in self._topological() if item in seen]

    def dependents(self, name: str) -> list[str]:
        key = self.get_skill(name).name.casefold()
        found = [other for other in self._skills if key in self._closure(other)]
        return sorted(self._skills[item].name for item in found)

    def ready_skills(self, completed: set[str] | None = None) -> list[str]:
        done = {item.casefold() for item in completed or set()}
        ready = [key for key, needs in self._requires.items() if key not in done and needs <= done]
        return sorted(self._skills[item].name for item in ready)

    def order(self) -> list[str]:
        return [self._skills[item].name for item in self._topological()]

    def skills(self) -> list[Skill]:
        return [self._skills[item] for item in sorted(self._skills)]

    def validate(self) -> list[str]:
        issues = []
        if self._has_cycle():
            issues.append("cycle")
        for key, needs in sorted(self._requires.items()):
            for need in sorted(needs):
                if need not in self._skills:
                    issues.append(f"missing prerequisite {need} for {key}")
        for skill in self.skills():
            if skill.status == SkillStatus.VALIDATED and not any(item.passed for item in skill.evidence):
                issues.append(f"validated without evidence: {skill.name}")
        return issues

    def _closure(self, key: str) -> set[str]:
        seen: set[str] = set()
        stack = list(self._requires[key])
        while stack:
            current = stack.pop()
            if current not in seen:
                seen.add(current)
                stack.extend(self._requires.get(current, set()))
        return seen

    def _has_cycle(self) -> bool:
        state: dict[str, int] = {}

        def visit(node: str) -> bool:
            state[node] = 1
            for nxt in self._requires.get(node, set()):
                if state.get(nxt) == 1:
                    return True
                if state.get(nxt) is None and visit(nxt):
                    return True
            state[node] = 2
            return False

        return any(state.get(node) is None and visit(node) for node in sorted(self._requires))

    def _topological(self) -> list[str]:
        ordered: list[str] = []
        remaining = {key: set(needs) for key, needs in self._requires.items()}
        while remaining:
            ready = sorted(key for key, needs in remaining.items() if needs <= set(ordered))
            if not ready:
                raise ValueError("Prerequisite cycle")
            ordered.append(ready[0])
            remaining.pop(ready[0])
        return ordered
