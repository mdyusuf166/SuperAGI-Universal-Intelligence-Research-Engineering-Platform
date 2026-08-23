from superagi.personal import *
from superagi.orchestration import *
def test_profile_goals_memory_and_personal_agi():
 pm=PersonalProfileManager();p=pm.create("User");assert pm.update(p.id,{"format":"concise"}).version==2
 goals=GoalManager();g=goals.create("research",milestones=["validate"]);assert g.milestones[0].name=="validate"
 reg=AgentCapabilityRegistry();reg.register(AgentDescriptor(name="research",capability=AgentCapability(domain="research",capabilities=["literature_analysis"])))
 agi=PersonalAGI(UniversalIntelligenceCoordinator(reg));result=agi.handle("Plan milestone",["literature_analysis"]);assert result["orchestration"].status=="VERIFIED"
def test_memory_requires_consent():
 from superagi.memory import UniversalMemory
 service=PersonalMemoryService(UniversalMemory())
 try:service.remember("private")
 except PermissionError:pass
 else:assert False
