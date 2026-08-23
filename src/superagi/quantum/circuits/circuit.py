from ..models import QuantumCircuit,QuantumOperation
class CircuitEngine:
 def create(self,nq,nc=0): return QuantumCircuit(num_qubits=nq,num_clbits=nc)
 def add_gate(self,circuit,gate,*qubits,parameters=()):
  return circuit.model_copy(update={"operations":circuit.operations+[QuantumOperation(gate=gate,qubits=list(qubits),parameters=list(parameters))]})
