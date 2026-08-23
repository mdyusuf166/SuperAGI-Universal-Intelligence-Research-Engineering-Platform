from dataclasses import dataclass
@dataclass(frozen=True)
class RoboticsSafetyDecision:allowed:bool;mode:str;reason:str
class RoboticsSafetyPolicy:
 def assess(self,command,approved=False):
  return RoboticsSafetyDecision(False,"SIMULATION_ONLY","Physical action requires explicit adapter configuration and approval.") if command.requires_approval and not approved else RoboticsSafetyDecision(True,"SIMULATION_ONLY","Simulation command accepted.")
