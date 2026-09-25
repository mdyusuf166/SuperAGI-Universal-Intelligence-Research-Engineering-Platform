from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..decisions import DecisionSupport


class DecisionSupportAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="decision_support_agent", description="Transparent decision support without making the decision", capabilities=("decision_support", "collaboration"), risk_level="low"))

    async def run(self, task, context):
        prepared = DecisionSupport().prepare(question=context.values["question"], options=context.values["options"], criteria=context.values.get("criteria", []), evidence=context.values.get("evidence", []), assumptions=context.values.get("assumptions", []), risks=context.values.get("risks", []), tradeoffs=context.values.get("tradeoffs", ""))
        return AgentResult(success=prepared["decision"].approved is False, confidence=0.3, summary="Decision support proposal. The human decides.", output={"agent": self.metadata.name, "question": prepared["decision"].question, "recommendation": prepared["recommendation"].text, "alternatives": prepared["recommendation"].alternatives, "uncertainty": prepared["decision"].uncertainty, "status": prepared["decision"].status, "executed": False}, limitations=["This is not objective correctness and is not an approved action."])
