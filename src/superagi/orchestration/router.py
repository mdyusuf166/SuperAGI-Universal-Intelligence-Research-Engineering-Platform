from .models import AgentSelection
class UniversalAgentRouter:
 def __init__(self,registry):self.registry=registry
 def route(self,request):
  agents=self.registry.discover(request.capabilities);return AgentSelection(agents=agents,status="AVAILABLE" if agents else "UNAVAILABLE",reason="Capability match" if agents else "No registered suitable agent")
