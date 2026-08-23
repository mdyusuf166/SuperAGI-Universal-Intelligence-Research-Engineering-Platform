from __future__ import annotations
from uuid import UUID,uuid4
from pydantic import BaseModel,ConfigDict,Field,model_validator
class QM(BaseModel): model_config=ConfigDict(extra="forbid")
class QuantumOperation(QM): gate:str; qubits:list[int]; parameters:list[float]=Field(default_factory=list)
class QuantumCircuit(QM):
 id:UUID=Field(default_factory=uuid4); num_qubits:int=Field(gt=0); num_clbits:int=0; operations:list[QuantumOperation]=Field(default_factory=list); metadata:dict=Field(default_factory=dict)
 @model_validator(mode="after")
 def valid(self):
  allowed={"X","Y","Z","H","S","T","CX","CZ","RX","RY","RZ","SWAP","MEASURE"}
  if any(o.gate not in allowed or any(q<0 or q>=self.num_qubits for q in o.qubits) for o in self.operations): raise ValueError("Invalid quantum gate or qubit")
  return self
class QuantumExperiment(QM): id:UUID=Field(default_factory=uuid4); circuit:QuantumCircuit; backend:str="mock"; shots:int=Field(default=1024,gt=0); seed:int|None=None
class QuantumResult(QM): experiment_id:UUID; status:str; counts:dict[str,int]=Field(default_factory=dict); probabilities:dict[str,float]=Field(default_factory=dict); backend:str; shots:int; is_simulation:bool=True; limitations:list[str]=Field(default_factory=list)
class QuantumAlgorithmResult(QM): algorithm:str; input:dict=Field(default_factory=dict); output:dict=Field(default_factory=dict); metrics:dict=Field(default_factory=dict); verification:dict=Field(default_factory=dict); limitations:list[str]=Field(default_factory=list)
