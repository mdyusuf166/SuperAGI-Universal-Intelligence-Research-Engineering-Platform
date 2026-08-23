from superagi.memory import UniversalMemory
from superagi.orchestration import IntelligenceRequest,UniversalIntelligenceCoordinator
from .models import *
from .services import *
class PersonalAGI:
 def __init__(self,orchestrator):self.orchestrator=orchestrator;self.memory=PersonalMemoryService(UniversalMemory());self.profiles=PersonalProfileManager();self.goals=GoalManager();self.projects=ProjectManager();self.learning=LearningManager()
 def handle(self,request,capabilities=()):
  session=PersonalSession(request=request);context=PersonalContext(goals=list(self.goals.goals.values())[:5],projects=list(self.projects.projects.values())[:5])
  plan=PersonalPlan(tasks=[PersonalTask(title="Review next active milestone",priority=1)],required_capabilities=list(capabilities),limitations=["Personal plan is a recommendation, not autonomous action."])
  report=self.orchestrator.solve(IntelligenceRequest(goal=request,capabilities=list(capabilities)))
  session.status="COMPLETED";session.results={"report_id":str(report.id)}
  recommendation=PersonalRecommendation(text="Review the highest-priority active milestone.",reason="Based on explicitly created goals.",confidence=.6,limitations=["User should review this recommendation."])
  return {"session":session,"context":context,"plan":plan,"orchestration":report,"recommendation":recommendation}
