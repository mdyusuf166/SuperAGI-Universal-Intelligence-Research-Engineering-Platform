from abc import ABC,abstractmethod
from .models import SimulationResult
class SimulationBackend(ABC):
 name="backend";capabilities=();availability=False
 @property
 def available(self): return self.availability
 @abstractmethod
 def simulate(self,proposal): ...
class UnavailableSimulationBackend(SimulationBackend):
 def __init__(self,name="unavailable",capabilities=()): self.name=name;self.capabilities=tuple(capabilities)
 def simulate(self,proposal): return SimulationResult(backend=self.name,status="UNAVAILABLE",limitations=["Requested real simulation backend is unavailable; no mock substituted."])
class MockSimulationBackend(SimulationBackend):
 name="mock";capabilities=("deterministic_test",);availability=True
 def simulate(self,proposal): return SimulationResult(backend=self.name,status="SIMULATION_RESULT",output={"proposal":proposal.objective,"variable_count":len(proposal.variables)},limitations=["Deterministic mock simulation for tests only; not a real simulator or laboratory validation."])
