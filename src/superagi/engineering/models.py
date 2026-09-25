from __future__ import annotations
from enum import Enum
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field
class EM(BaseModel): model_config=ConfigDict(extra="forbid")
class EngineeringDomain(str,Enum): SYSTEMS="Systems Engineering";COMPUTER="Computer Engineering";ELECTRICAL="Electrical Engineering";ELECTRONICS="Electronics";CIRCUIT="Circuit Design";EMBEDDED="Embedded Systems";ROBOTICS="Robotics Engineering";CONTROL="Control Engineering";SOFTWARE="Software Engineering";MECHANICAL="Mechanical Engineering";AEROSPACE="Aerospace Engineering";INFRASTRUCTURE="Infrastructure Engineering";MATERIALS="Materials Engineering";AI="AI Engineering";QUANTUM="Quantum Engineering"
class EngineeringRequirement(EM): id:UUID=Field(default_factory=uuid4);statement:str;category:str="functional";priority:int=1;measurable:bool=True;verification_method:str="review";constraints:list[str]=Field(default_factory=list);source:str="user"
class EngineeringConstraint(EM): id:UUID=Field(default_factory=uuid4);kind:str;limit:str;source:str="user"
class SystemComponent(EM): id:UUID=Field(default_factory=uuid4);name:str;kind:str="component";interfaces:list[str]=Field(default_factory=list);dependencies:list[str]=Field(default_factory=list);verified:bool=False
class SystemInterface(EM): name:str;source:str;target:str;protocol:str="conceptual";compatible:bool=True
class Subsystem(EM): name:str;components:list[SystemComponent]=Field(default_factory=list)
class SystemArchitecture(EM): name:str;subsystems:list[Subsystem]=Field(default_factory=list);interfaces:list[SystemInterface]=Field(default_factory=list)
class EngineeringDesign(EM): id:UUID=Field(default_factory=uuid4);problem:str;requirements:list[EngineeringRequirement]=Field(default_factory=list);architecture:SystemArchitecture;components:list[SystemComponent]=Field(default_factory=list);interfaces:list[SystemInterface]=Field(default_factory=list);assumptions:list[str]=Field(default_factory=list);constraints:list[EngineeringConstraint]=Field(default_factory=list);decisions:list[str]=Field(default_factory=list);verification_status:str="UNVERIFIED";provenance:list[str]=Field(default_factory=list)
class TradeoffAnalysis(EM): criteria:dict[str,float]=Field(default_factory=dict);recommendation:str;reason:str
class VerificationResult(EM): status:str;checks:dict[str,bool]=Field(default_factory=dict);limitations:list[str]=Field(default_factory=list)
class EngineeringSimulationResult(EM): backend:str;status:str;output:dict=Field(default_factory=dict);limitations:list[str]=Field(default_factory=list)
class ReviewSeverity(str,Enum): INFO="INFO";WARNING="WARNING";ERROR="ERROR";CRITICAL="CRITICAL"
class ReviewFinding(EM): category:str;message:str;severity:ReviewSeverity
class DesignReviewReport(EM): issues:list[str]=Field(default_factory=list);status:str="PARTIALLY_VERIFIED";findings:list[ReviewFinding]=Field(default_factory=list);accepted:bool=True
class ComputerArchitecture(EM): cpu:str;memory:str;bus:str;io:list[str]=Field(default_factory=list);storage:str="";network_interface:str=""
class EmbeddedSystemDesign(EM): microcontroller:str;io:list[str]=Field(default_factory=list);timers:int=0;mode:str="SIMULATION_PROPOSAL_ONLY"
class ControlDesign(EM): setpoint:float;pid:tuple[float,float,float]=(0.,0.,0.);sensor_model:str="conceptual";actuator_model:str="conceptual";status:str="SIMULATION CONTROL"
