from __future__ import annotations
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field
class PM(BaseModel):model_config=ConfigDict(extra="forbid")
class PersonalProfile(PM):id:UUID=Field(default_factory=uuid4);name:str;preferences:dict=Field(default_factory=dict);version:int=1
class UserPreference(PM):id:UUID=Field(default_factory=uuid4);key:str;value:str
class GoalMilestone(PM):id:UUID=Field(default_factory=uuid4);name:str;status:str="PENDING"
class UserGoal(PM):id:UUID=Field(default_factory=uuid4);title:str;priority:int=0;status:str="ACTIVE";milestones:list[GoalMilestone]=Field(default_factory=list)
class PersonalTask(PM):id:UUID=Field(default_factory=uuid4);title:str;status:str="PENDING";priority:int=0
class PersonalProject(PM):id:UUID=Field(default_factory=uuid4);name:str;description:str="";tasks:list[PersonalTask]=Field(default_factory=list);status:str="ACTIVE"
class LearningObjective(PM):id:UUID=Field(default_factory=uuid4);topic:str;completed_topics:list[str]=Field(default_factory=list);progress:float=0
class PersonalContext(PM):goals:list[UserGoal]=Field(default_factory=list);projects:list[PersonalProject]=Field(default_factory=list);preferences:dict=Field(default_factory=dict);memories:list[str]=Field(default_factory=list)
class PersonalRecommendation(PM):id:UUID=Field(default_factory=uuid4);text:str;reason:str;confidence:float;limitations:list[str]=Field(default_factory=list)
class PersonalPlan(PM):id:UUID=Field(default_factory=uuid4);tasks:list[PersonalTask]=Field(default_factory=list);required_capabilities:list[str]=Field(default_factory=list);limitations:list[str]=Field(default_factory=list)
class PersonalSession(PM):id:UUID=Field(default_factory=uuid4);request:str;status:str="ACTIVE";results:dict=Field(default_factory=dict)
class PersonalDecision(PM):id:UUID=Field(default_factory=uuid4);options:list[str];criteria:list[str];recommendation:str|None=None;limitations:list[str]=Field(default_factory=list)
