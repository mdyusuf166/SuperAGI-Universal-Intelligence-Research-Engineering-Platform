from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata, AgentResult
from superagi.science.pipeline import SciencePipeline
class ScienceAgent(BaseAgent):
 def __init__(self): super().__init__(AgentMetadata(name="science_agent",description="Proposal-only scientific synthesis",capabilities=("science","scientific_synthesis"),risk_level="low"))
 async def run(self,task,context):
  result=SciencePipeline().run(context.values["scientific_question"])
  return AgentResult(success=True,confidence=.2,summary="Structured scientific proposal; no private reasoning or real-world execution.",output={"status":result["status"],"report":result.get("report").model_dump(mode="json") if result.get("report") else {}})
