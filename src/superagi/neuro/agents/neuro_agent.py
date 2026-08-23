from superagi.core.agents import BaseAgent
from superagi.core.models import AgentContext, AgentResult, Task, AgentMetadata
from ..signals import SpikeTrainAnalyzer
class NeuroResearchAgent(BaseAgent):
    def __init__(self): super().__init__(AgentMetadata(name="neuro_research",description="Computational neuroscience agent",capabilities=("simulation","spike analysis")))
    async def run(self, task:Task, context:AgentContext):
        trains=context.values.get("spikes",[]); metrics={"population_rate":SpikeTrainAnalyzer().population_rate(trains)} if trains else {}
        return AgentResult(success=True,output={"classification":"COMPUTATIONAL_OBSERVATION","metrics":metrics},summary="Neuro computational analysis.",limitations=["No cognitive, disease, or clinical inference."])
