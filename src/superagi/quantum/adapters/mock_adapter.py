from ..models import QuantumResult
class MockQuantumAdapter:
 available=True
 def run(self,experiment):
  bits="0"*experiment.circuit.num_qubits; counts={bits:experiment.shots}
  return QuantumResult(experiment_id=experiment.id,status="SIMULATION_RESULT",counts=counts,probabilities={bits:1.0},backend="mock",shots=experiment.shots,limitations=["Deterministic mock simulation; no quantum hardware result or advantage claim."])
