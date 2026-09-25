from superagi.core.models import AgentResult

from ..models import ComputerArchitecture
from .engineering_agent import EngineeringAgent


class ArchitectureAgent(EngineeringAgent):
    def __init__(self):
        super().__init__("architecture_agent", ("engineering", "architecture"))

    async def run(self, task, context):
        computer = context.values.get("computer")
        if computer is None:
            return await super().run(task, context)
        architecture = computer if isinstance(computer, ComputerArchitecture) else ComputerArchitecture(**computer)
        return AgentResult(
            success=True,
            confidence=0.3,
            summary="Conceptual computer architecture; not a manufactured machine.",
            output={"agent": self.metadata.name, "classification": "CONCEPTUAL", "architecture": architecture.model_dump()},
            limitations=["Conceptual computer architecture only."],
        )
