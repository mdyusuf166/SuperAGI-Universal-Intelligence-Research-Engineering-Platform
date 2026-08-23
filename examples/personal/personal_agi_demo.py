from superagi.personal import PersonalAGI
from superagi.orchestration import *
r=AgentCapabilityRegistry();r.register(AgentDescriptor(name="research",capability=AgentCapability(domain="research",capabilities=["literature_analysis"])))
agi=PersonalAGI(UniversalIntelligenceCoordinator(r));profile=agi.profiles.create("Demo User");agi.profiles.update(profile.id,{"style":"concise"});agi.goals.create("Research milestone",milestones=["Architecture","Validation"]);agi.projects.create("SuperAGI",tasks=["Test ARC-10"])
result=agi.handle("Plan my next research milestone and identify specialized agents.",["literature_analysis"])
print("PROFILE\nGOALS\nPROJECTS\nPERSONAL CONTEXT\nPLAN\nAGENT ROUTING\nTASK GRAPH\nRESULTS\nMEMORY\nVERIFICATION\nFINAL PERSONAL INTELLIGENCE REPORT\n",result["recommendation"].model_dump())
