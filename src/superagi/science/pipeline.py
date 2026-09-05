from .domains import classify_domains
from .knowledge import KnowledgeSynthesizer
from .hypothesis import HypothesisGenerator,HypothesisCritic
from .experiment import ExperimentDesigner
from .simulation import MockSimulationBackend,UnavailableSimulationBackend
from .safety import ScientificSafetyPolicy
from .evaluation import metrics
from .models import KnowledgeItem,KnowledgeKind,ScientificReport
class SciencePipeline:
 def __init__(self,memory=None,simulation_backend=None): self.memory=memory;self.simulation_backend=simulation_backend or MockSimulationBackend();self.cancelled=False
 def cancel(self): self.cancelled=True
 def run(self,q):
  if self.cancelled: return {"status":"CANCELLED","reason":"Pipeline cancellation requested."}
  ScientificSafetyPolicy().require_safe(q.question)
  q.domain=classify_domains(q.question,q.domain);knowledge=KnowledgeSynthesizer(self.memory).synthesize(q);hypothesis=HypothesisGenerator().generate(q);critique=HypothesisCritic().critique(hypothesis);experiment=ExperimentDesigner().design(q,hypothesis);simulation=self.simulation_backend.simulate(experiment);report=ScientificReport(question=q,summary="Proposal-only scientific synthesis; no discovery, proof, laboratory execution, or clinical conclusion.",conclusions=[KnowledgeItem(statement=hypothesis.hypothesis,kind=KnowledgeKind.HYPOTHESIS,evidence_refs=hypothesis.supporting_evidence,provenance_refs=q.provenance_refs)],limitations=["Generated hypothesis is explicitly unproven.",*simulation.limitations],provenance_refs=q.provenance_refs)
  return {"status":"COMPLETED","question":q,"domains":q.domain,"knowledge":knowledge,"hypothesis":hypothesis,"critique":critique,"experiment":experiment,"simulation":simulation,"metrics":metrics(q,knowledge,hypothesis,critique),"report":report}
