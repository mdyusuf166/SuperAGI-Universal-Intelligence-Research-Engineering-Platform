from .models import Hypothesis,HypothesisStatus,ScientificQuestion
class HypothesisGenerator:
 def generate(self,q:ScientificQuestion):
  variables=", ".join(q.variables) or "the stated variables"; return Hypothesis(hypothesis=f"PROPOSED HYPOTHESIS: Changes in {variables} may influence the observed outcome.",rationale="Deterministic proposal derived from declared variables; it is not a finding.",supporting_evidence=q.evidence_refs,assumptions=q.assumptions,predicted_observations=["The measured outcome changes when one declared variable is varied under controls."],confounders=q.unknowns,confidence=.2 if q.evidence_refs else .1,status=HypothesisStatus.PROPOSED)
class HypothesisEvaluator:
 def evaluate(self,h): return round(min(1.,h.confidence+.1*len(h.supporting_evidence)-.1*len(h.contradictory_evidence)),2)
class HypothesisCritic:
 def critique(self,h): return {"status":HypothesisStatus.CONTRADICTED.value if h.contradictory_evidence else HypothesisStatus.UNTESTED.value,"issues":["No experimental validation; hypothesis remains unproven."]+([] if h.supporting_evidence else ["No linked supporting evidence."]),"contradictory_evidence":h.contradictory_evidence}
