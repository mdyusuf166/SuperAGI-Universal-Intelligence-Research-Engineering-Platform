from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..models import ReviewSeverity
from ..services import DesignReview


class DesignReviewAgent(BaseAgent):
    def __init__(self, name="design_review_agent", capabilities=("engineering", "design_review")):
        super().__init__(AgentMetadata(name=name, description="Deterministic design review using the engineering design review service", capabilities=capabilities, risk_level="low"))
        self.reviewer = DesignReview()

    async def run(self, task, context):
        report = self.reviewer.review(context.values["design"], simulation=context.values.get("simulation"), risks=context.values.get("risks"))
        critical = [finding.message for finding in report.findings if finding.severity == ReviewSeverity.CRITICAL]
        return AgentResult(
            success=report.accepted and not critical,
            confidence=0.4 if report.accepted else 0.1,
            summary="Design review findings. No hidden reasoning trace.",
            output={
                "agent": self.metadata.name,
                "status": report.status,
                "accepted": report.accepted,
                "issues": report.issues,
                "findings": [finding.model_dump() for finding in report.findings],
                "critical": critical,
            },
            limitations=["Conceptual review only. This is not safety certification."],
        )
