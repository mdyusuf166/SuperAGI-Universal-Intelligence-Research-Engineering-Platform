from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from .models import AgentContext, AgentMetadata, AgentResult, AgentStatus, Task


class BaseAgent(ABC):
    def __init__(self, metadata: AgentMetadata) -> None:
        self.metadata = metadata
        self.status = AgentStatus.CREATED

    @property
    def id(self) -> UUID:
        return self.metadata.id

    @abstractmethod
    async def run(self, task: Task, context: AgentContext) -> AgentResult:
        """Execute a task without exposing private reasoning traces."""


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        if agent.metadata.name in self._agents:
            raise ValueError(f"Agent already registered: {agent.metadata.name}")
        self._agents[agent.metadata.name] = agent

    def unregister(self, name: str) -> BaseAgent:
        try:
            return self._agents.pop(name)
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {name}") from exc

    def get(self, name: str) -> BaseAgent:
        return self._agents[name]

    def list(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def exists(self, name: str) -> bool:
        return name in self._agents
