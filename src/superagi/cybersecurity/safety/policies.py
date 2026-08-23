from dataclasses import dataclass
@dataclass(frozen=True)
class CyberSafetyDecision:allowed:bool;mode:str;reason:str
class CyberSafetyPolicy:
 def assess(self,text):
  banned=("exploit","malware","credential","scan external","destructive")
  return CyberSafetyDecision(False,"LOCAL_LAB_ONLY","Rejected offensive or external-target action.") if any(x in text.lower() for x in banned) else CyberSafetyDecision(True,"LOCAL_LAB_ONLY","Defensive local analysis only.")
