from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..models import InteractionMode
from ..pipeline import CollaborationPipeline
from ..roles import RoleAssigner


class CollaborationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="collaboration_agent", description="Bounded human-AI collaboration assistance", capabilities=("collaboration", "personal"), risk_level="low"))

    async def run(self, task, context):
        values = context.values
        result = CollaborationPipeline(memory=values.get("memory")).run(
            values["objective"],
            participants=values.get("participants", []),
            roles=values.get("roles", [RoleAssigner().assign("human", "decision_maker", human=True)]),
            consent=values["consent"],
            mode=values.get("mode", InteractionMode.AI_ASSISTED),
            goal_statements=values.get("goal_statements", [values["objective"]]),
            task_specs=values.get("task_specs", [{"title": "Review the draft", "owner": "human", "completion_criteria": ["Human review"], "evidence": ["user-supplied session"]}]),
            constraints=tuple(values.get("constraints", ())),
            evidence=tuple(values.get("evidence", ("user-supplied session",))),
            sources=tuple(values.get("sources", ("user-supplied session",))),
            registry=values.get("registry"),
            capabilities=tuple(values.get("capabilities", ("collaboration",))),
            approval=bool(values.get("approval", False)),
        )
        return AgentResult(success=result["status"] in {"COMPLETED", "AWAITING_HUMAN_APPROVAL"}, confidence=0.3, summary="Collaboration report. No external action was executed.", output={"agent": self.metadata.name, "status": result["status"], "executed": result["executed"], "report": result["report"]}, limitations=["Assistance only. The human remains the decision maker."])
