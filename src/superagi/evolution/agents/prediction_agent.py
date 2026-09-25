from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult

from ..prediction import PredictionEngine


class PredictionAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(AgentMetadata(name="prediction_agent", description="Deterministic baseline prediction", capabilities=("prediction", "evolution"), risk_level="low"))

    async def run(self, task, context):
        output = PredictionEngine().predict(context.values["request"])
        return AgentResult(success=output.status.value == "PREDICTED", confidence=output.confidence.value, summary="Baseline prediction. Not a measured forecast accuracy.", output={"agent": self.metadata.name, "method": output.method.value, "values": [point.value for point in output.points], "measured_accuracy": output.confidence.measured_accuracy}, limitations=output.limitations)
