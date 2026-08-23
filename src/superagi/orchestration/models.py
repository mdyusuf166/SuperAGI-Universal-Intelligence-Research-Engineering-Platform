from __future__ import annotations
from datetime import datetime,timezone
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field
class OM(BaseModel):model_config=ConfigDict(extra="forbid")
class IntelligenceRequest(OM):id:UUID=Field(default_factory=uuid4);goal:str;capabilities:list[str]=Field(default_factory=list);risk_level:str="low";execution_mode:str="COMPUTATIONAL"
class IntelligenceGoal(OM):id:UUID=Field(default_factory=uuid4);request_id:UUID;description:str;status:str="created";created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
class AgentCapability(OM):domain:str;capabilities:list[str]=Field(default_factory=list);task_types:list[str]=Field(default_factory=list);safety_level:str="low";available:bool=True
class AgentDescriptor(OM):id:UUID=Field(default_factory=uuid4);name:str;capability:AgentCapability;specialized:bool=True
class AgentSelection(OM):agents:list[AgentDescriptor]=Field(default_factory=list);status:str="AVAILABLE";reason:str=""
class OrchestrationTask(OM):id:UUID=Field(default_factory=uuid4);name:str;capabilities:list[str]=Field(default_factory=list);dependencies:list[UUID]=Field(default_factory=list);priority:int=0;status:str="PENDING";risk_level:str="low"
class TaskGraph(OM):id:UUID=Field(default_factory=uuid4);tasks:list[OrchestrationTask]=Field(default_factory=list)
class TaskResult(OM):task_id:UUID;status:str;output:dict=Field(default_factory=dict);provenance:list[str]=Field(default_factory=list);limitations:list[str]=Field(default_factory=list)
class TaskDependency(OM):task_id:UUID;depends_on:UUID
class AgentResult(OM):agent_id:UUID|None=None;task_id:UUID;status:str;output:dict=Field(default_factory=dict);evidence:list[str]=Field(default_factory=list);provenance:list[str]=Field(default_factory=list)
class EvidenceReference(OM):id:UUID=Field(default_factory=uuid4);reference:str;source:str;status:str="SUPPORTED"
class ConfidenceAssessment(OM):value:float=Field(ge=0,le=1);reason:str="";limitations:list[str]=Field(default_factory=list)
class OrchestrationTrace(OM):id:UUID=Field(default_factory=uuid4);request_id:UUID;events:list[str]=Field(default_factory=list);status:str="created";created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
class OrchestrationMetrics(OM):completed_tasks:int=0;failed_tasks:int=0;cancelled_tasks:int=0;evidence_count:int=0;conflict_count:int=0
class Conflict(OM):conflict_id:UUID=Field(default_factory=uuid4);source_results:list[UUID]=Field(default_factory=list);description:str;severity:str="low";resolution_status:str="OPEN"
class VerificationResult(OM):status:str;checks:dict=Field(default_factory=dict);limitations:list[str]=Field(default_factory=list)
class IntelligenceReport(OM):id:UUID=Field(default_factory=uuid4);request_id:UUID;status:str;task_results:list[TaskResult]=Field(default_factory=list);conflicts:list[Conflict]=Field(default_factory=list);verification:VerificationResult;limitations:list[str]=Field(default_factory=list)
