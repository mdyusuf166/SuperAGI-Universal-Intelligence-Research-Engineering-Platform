from superagi.core.models import AgentResult

from ..embedded import PROPOSAL_ONLY, EmbeddedValidator
from .engineering_agent import EngineeringAgent


class EmbeddedAgent(EngineeringAgent):
    def __init__(self):
        super().__init__("embedded_agent", ("engineering", "embedded_design"))

    async def run(self, task, context):
        embedded = context.values.get("embedded")
        if embedded is None:
            return await super().run(task, context)
        validation = EmbeddedValidator().validate(embedded)
        return AgentResult(
            success=validation.valid,
            confidence=0.3,
            summary="Embedded proposal validation; no device execution.",
            output={"agent": self.metadata.name, "mode": PROPOSAL_ONLY, "validation": validation.model_dump()},
            limitations=["PROPOSAL_ONLY. No physical-device execution."],
        )
