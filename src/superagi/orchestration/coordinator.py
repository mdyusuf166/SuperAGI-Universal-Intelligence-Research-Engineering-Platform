from superagi.memory import UniversalMemory
from .models import IntelligenceGoal,IntelligenceReport
from .router import UniversalAgentRouter
from .planner import UniversalTaskPlanner
from .executor import MultiAgentExecutor,ResultAggregator,UniversalVerifier
class UniversalIntelligenceCoordinator:
 def __init__(self,registry,memory=None):self.registry=registry;self.memory=memory or UniversalMemory();self.router=UniversalAgentRouter(registry)
 def solve(self,request):
  if request.execution_mode not in {"COMPUTATIONAL","SIMULATION"}:raise PermissionError("Physical/external execution is denied by default")
  goal=IntelligenceGoal(request_id=request.id,description=request.goal);selection=self.router.route(request);graph=UniversalTaskPlanner().plan(request);results=MultiAgentExecutor().execute(graph,selection);conflicts=ResultAggregator().conflicts(results);verification=UniversalVerifier().verify(results)
  report=IntelligenceReport(request_id=request.id,status=verification.status,task_results=results,conflicts=conflicts,verification=verification,limitations=["Proposal/computation only; not real-world execution or proof. Conflicts are surfaced, not silently resolved."])
  self.memory.remember(str(report.model_dump()),source="orchestration",source_id=str(goal.id),metadata={"classification":"COMPUTATIONAL_RESULT"});return report
