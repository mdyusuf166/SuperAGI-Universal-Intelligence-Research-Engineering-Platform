from ..models import QuantumExperiment,QuantumResult
from ..adapters import MockQuantumAdapter
class QuantumSimulationEngine:
 def __init__(self,adapters=None):self.adapters=adapters or {"mock":MockQuantumAdapter()}
 def run(self,experiment):
  adapter=self.adapters.get(experiment.backend)
  if adapter is None or not adapter.available:return QuantumResult(experiment_id=experiment.id,status="UNAVAILABLE",backend=experiment.backend,shots=experiment.shots,limitations=["Requested backend unavailable; no substitute used."])
  return adapter.run(experiment)
