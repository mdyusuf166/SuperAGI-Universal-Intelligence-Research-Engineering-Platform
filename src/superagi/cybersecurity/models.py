from __future__ import annotations
from datetime import datetime,timezone
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field
class SM(BaseModel):model_config=ConfigDict(extra="forbid")
class Asset(SM):id:UUID=Field(default_factory=uuid4);name:str;asset_type:str;environment:str="local_lab";owner:str="";criticality:float=0.5;metadata:dict=Field(default_factory=dict)
class SecurityEvent(SM):id:UUID=Field(default_factory=uuid4);timestamp:datetime=Field(default_factory=lambda:datetime.now(timezone.utc));source:str;event_type:str;severity:str="low";message:str="";metadata:dict=Field(default_factory=dict)
class Threat(SM):id:UUID=Field(default_factory=uuid4);name:str;category:str;description:str="";likelihood:float=0;impact:float=0
class Vulnerability(SM):id:UUID=Field(default_factory=uuid4);asset_id:UUID;title:str;description:str="";severity:str;confidence:float;evidence:list[str]=Field(default_factory=list);remediation:str=""
class SecurityFinding(SM):id:UUID=Field(default_factory=uuid4);category:str;severity:str;confidence:float;evidence:list[str]=Field(default_factory=list);recommendation:str="";limitations:list[str]=Field(default_factory=list)
class SecurityAlert(SM):id:UUID=Field(default_factory=uuid4);rule_id:str;severity:str;event_ids:list[UUID]=Field(default_factory=list);reason:str;status:str="open"
class Incident(SM):id:UUID=Field(default_factory=uuid4);title:str;severity:str;events:list[SecurityEvent]=Field(default_factory=list);findings:list[SecurityFinding]=Field(default_factory=list);timeline:list[SecurityEvent]=Field(default_factory=list);status:str="investigating"
class RiskAssessment(SM):asset_id:UUID;likelihood:float;impact:float;risk_score:float;reasoning:str;mitigations:list[str]=Field(default_factory=list)
