from ..models import SecurityFinding
class CodeSecurityAnalyzer:
 def analyze(self,text):
  patterns=[("hardcoded_secret","password=", "Remove hardcoded secrets and use a secret manager."),("unsafe_eval","eval(","Avoid eval; use safe parsing."),("dangerous_shell","shell=True","Avoid shell execution; use argument lists.")]
  return [SecurityFinding(category=x,severity="high",confidence=1,evidence=[x],recommendation=r,limitations=["Static pattern analysis only."]) for x,p,r in patterns if p in text]
