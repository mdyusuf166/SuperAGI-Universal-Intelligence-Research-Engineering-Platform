from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult, Task
from superagi.core.planning import PlanExecutor, Planner

from ..goals import GoalService


class PlanningAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="planning_agent", description="Composes ARC-01 plans with collaboration goals", capabilities=("planning", "collaboration"), risk_level="low"))

    async def run(self, task, context):
        statement = context.values["goal"]
        constraints = list(context.values.get("constraints", []))
        milestones = list(context.values.get("milestones", []))
        criteria = list(context.values.get("verification_criteria", ["Human review"]))
        goal = GoalService().create(statement, milestones=tuple(milestones))
        core = Task(description=statement)
        plan = Planner().create_plan(core)

        async def handler(step):
            return {"step": step.step_id, "draft": True}

        await PlanExecutor().execute(plan, handler)
        return AgentResult(success=True, confidence=0.3, summary="Draft plan composed with the core planner.", output={"agent": self.metadata.name, "goal": goal.statement, "constraints": constraints, "milestones": [item.name for item in goal.milestones], "steps": [step.description for step in plan.steps], "verification_criteria": criteria, "executed": False}, limitations=["The plan is a draft. It does not redefine the user goal."])
