from ..models import RiskAssessment
class RiskEngine:
 def assess(self,asset,likelihood,impact,confidence=1):return RiskAssessment(asset_id=asset.id,likelihood=likelihood,impact=impact,risk_score=round(likelihood*impact*asset.criticality*confidence,3),reasoning="Deterministic likelihood × impact × criticality × confidence.",mitigations=["Review local controls and investigate evidence."])
