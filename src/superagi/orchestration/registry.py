from .models import AgentDescriptor
class AgentCapabilityRegistry:
 def __init__(self):self._agents={}
 def register(self,agent):self._agents[agent.name]=agent
 def discover(self,capabilities,domain=None,task_type=None,required_tools=(),safety_level=None):
  return [a for a in self._agents.values() if a.capability.available and set(capabilities)&set(a.capability.capabilities) and (domain is None or a.capability.domain==domain) and (safety_level is None or a.capability.safety_level==safety_level)]
