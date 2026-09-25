from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult


class ConflictDetectionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="conflict_detection_agent", description="Reports unresolved property and relation conflicts", capabilities=("conflict_detection", "world_model"), risk_level="low"))

    async def run(self, task, context):
        conflicts = context.values["graph"].detect_contradictions()
        return AgentResult(success=True, confidence=0.3, summary="Conflicts are exposed and left unresolved unless a caller supplies a rule.", output={"agent": self.metadata.name, "subjects": [item.subject for item in conflicts], "resolution": [item.resolution_status.value for item in conflicts], "executed": False}, limitations=["No conflicting value was selected."])
