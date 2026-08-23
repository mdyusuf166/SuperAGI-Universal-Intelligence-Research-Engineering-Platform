from superagi.orchestration import *
def test_end_to_end_orchestration():
 r=AgentCapabilityRegistry();r.register(AgentDescriptor(name="biomedical",capability=AgentCapability(domain="biomedical",capabilities=["molecular_analysis"])))
 request=IntelligenceRequest(goal="controlled analysis",capabilities=["molecular_analysis"]);report=UniversalIntelligenceCoordinator(r).solve(request);assert report.status=="VERIFIED" and report.task_results
def test_unavailable_agent():assert UniversalAgentRouter(AgentCapabilityRegistry()).route(IntelligenceRequest(goal="x",capabilities=["x"])).status=="UNAVAILABLE"
