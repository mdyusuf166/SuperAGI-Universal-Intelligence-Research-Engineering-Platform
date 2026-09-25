from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..models import ReviewSeverity
from ..services import CollaborationReview
from ..sessions import SessionStore


class ReviewAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="review_agent", description="Reviews collaboration artifacts without hidden reasoning", capabilities=("collaboration", "review"), risk_level="low"))

    async def run(self, task, context):
        session = context.values.get("session")
        if session is None:
            store = SessionStore(context.values.get("objective", ""))
            session = store.session
        report = CollaborationReview().review(session, approval_granted=bool(context.values.get("approval", False)), orchestration_conflicts=context.values.get("orchestration_conflicts"))
        critical = [item.message for item in report["findings"] if item.severity == ReviewSeverity.CRITICAL]
        return AgentResult(success=report["accepted"] and not critical, confidence=0.3, summary="Collaboration review findings.", output={"agent": self.metadata.name, "status": report["status"], "accepted": report["accepted"], "findings": [item.model_dump() for item in report["findings"]], "critical": critical}, limitations=["Review is not approval to act."])
