from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..planning import PlanningEngine


class PlanningAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="evolution_planning_agent", description="Deterministic planning proposals composed with ARC-01", capabilities=("planning", "evolution"), risk_level="low"))

    async def run(self, task, context):
        engine = PlanningEngine()
        plan = engine.plan(context.values["problem"])
        core_steps = await engine.execute_core(context.values["problem"].goal.statement)
        return AgentResult(success=plan.status == "PROPOSAL", confidence=0.3, summary="Planning proposal. Not an executed plan.", output={"agent": self.metadata.name, "status": plan.status, "steps": [step.step_id for step in plan.steps], "core_steps": core_steps, "feasible": plan.feasible, "executed": False}, limitations=["The plan is a proposal."])
