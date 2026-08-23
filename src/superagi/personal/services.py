from .models import *
class PersonalProfileManager:
 def __init__(self):self.profiles={}
 def create(self,name):p=PersonalProfile(name=name);self.profiles[p.id]=p;return p
 def update(self,id,preferences):p=self.profiles[id];p.preferences.update(preferences);p.version+=1;return p
class GoalManager:
 def __init__(self):self.goals={}
 def create(self,title,priority=0,milestones=()):g=UserGoal(title=title,priority=priority,milestones=[GoalMilestone(name=x) for x in milestones]);self.goals[g.id]=g;return g
 def complete(self,id):self.goals[id].status="COMPLETED";return self.goals[id]
class ProjectManager:
 def __init__(self):self.projects={}
 def create(self,name,description="",tasks=()):p=PersonalProject(name=name,description=description,tasks=[PersonalTask(title=x) for x in tasks]);self.projects[p.id]=p;return p
class LearningManager:
 def __init__(self):self.objectives={}
 def create(self,topic):x=LearningObjective(topic=topic);self.objectives[x.id]=x;return x
class PersonalMemoryService:
 def __init__(self,memory):self.memory=memory;self.allowed=False;self.ids=[]
 def allow_memory(self):self.allowed=True
 def deny_memory(self):self.allowed=False
 def remember(self,text,category="interaction summary"):
  if not self.allowed:raise PermissionError("Explicit memory permission is required")
  r=self.memory.remember(text,source="personal",metadata={"category":category});self.ids.append(r.id);return r
 def forget(self,id):return self.memory.forget(id)
