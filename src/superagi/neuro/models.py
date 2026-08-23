from __future__ import annotations
from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict, Field, field_validator
class NeuroModel(BaseModel): model_config = ConfigDict(extra="forbid")
class Neuron(NeuroModel): id: UUID = Field(default_factory=uuid4); model: str = "integrate_and_fire"; parameters: dict[str, float] = Field(default_factory=dict); metadata: dict = Field(default_factory=dict)
class Connection(NeuroModel): source_id: UUID; target_id: UUID; weight: float; delay: float = Field(ge=0)
class NeuronNetwork(NeuroModel):
    id: UUID = Field(default_factory=uuid4); neurons: list[Neuron] = Field(default_factory=list); connections: list[Connection] = Field(default_factory=list); parameters: dict = Field(default_factory=dict)
    def model_post_init(self, __context):
        ids={n.id for n in self.neurons}
        if any(c.source_id not in ids or c.target_id not in ids for c in self.connections): raise ValueError("Connections must reference neurons in the network")
class SpikeTrain(NeuroModel): neuron_id: UUID; timestamps: list[float] = Field(default_factory=list); duration: float = Field(gt=0); sampling_information: dict = Field(default_factory=dict)
class SimulationConfig(NeuroModel): duration: float = Field(gt=0); timestep: float = Field(gt=0); seed: int | None = None; backend: str = "mock"
class SimulationResult(NeuroModel): simulation_id: UUID = Field(default_factory=uuid4); status: str; metrics: dict = Field(default_factory=dict); spikes: list[SpikeTrain] = Field(default_factory=list); backend: str; limitations: list[str] = Field(default_factory=list); provenance: tuple[str, ...] = ()
class BrainRegion(NeuroModel): id: UUID = Field(default_factory=uuid4); name: str; description: str = ""; metadata: dict = Field(default_factory=dict)
class BrainArchitecture(NeuroModel): regions: list[BrainRegion] = Field(default_factory=list); connections: list[dict] = Field(default_factory=list); metadata: dict = Field(default_factory=dict)
class NeuroResearchResult(NeuroModel): observations: list[dict] = Field(default_factory=list); metrics: dict = Field(default_factory=dict); evidence: list[dict] = Field(default_factory=list); hypotheses: list[str] = Field(default_factory=list); limitations: list[str] = Field(default_factory=list); provenance: tuple[str, ...] = ()
