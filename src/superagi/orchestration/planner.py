from .models import OrchestrationTask,TaskGraph
class UniversalTaskPlanner:
 def plan(self,request):
  names=["question_analysis",*request.capabilities,"verification","synthesis"]; tasks=[]; previous=[]
  for name in names:
   task=OrchestrationTask(name=name,capabilities=[name],dependencies=previous);tasks.append(task);previous=[task.id]
  return TaskGraph(tasks=tasks)
