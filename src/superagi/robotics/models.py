from __future__ import annotations
from datetime import datetime,timezone
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field
class RM(BaseModel):model_config=ConfigDict(extra="forbid")
class Robot(RM):id:UUID=Field(default_factory=uuid4);name:str;robot_type:str="mobile";capabilities:list[str]=Field(default_factory=list);sensors:list[str]=Field(default_factory=list);actuators:list[str]=Field(default_factory=list);metadata:dict=Field(default_factory=dict)
class Pose(RM):x:float;y:float;z:float=0;roll:float=0;pitch:float=0;yaw:float=0
class SensorReading(RM):sensor_id:str;sensor_type:str;timestamp:datetime=Field(default_factory=lambda:datetime.now(timezone.utc));data:dict=Field(default_factory=dict);metadata:dict=Field(default_factory=dict)
class RobotState(RM):pose:Pose;velocity:float=0;battery:float=1;sensor_state:dict=Field(default_factory=dict);timestamp:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
class Waypoint(RM):x:float;y:float;z:float=0;tolerance:float=0.1
class Trajectory(RM):waypoints:list[Waypoint];timestamps:list[float]=Field(default_factory=list);velocity_limits:float=1;acceleration_limits:float=1
class RobotCommand(RM):command_type:str;parameters:dict=Field(default_factory=dict);requires_approval:bool=True
class SimulationResult(RM):simulation_id:UUID=Field(default_factory=uuid4);status:str;metrics:dict=Field(default_factory=dict);observations:list[dict]=Field(default_factory=list);is_simulation:bool=True;limitations:list[str]=Field(default_factory=list)
