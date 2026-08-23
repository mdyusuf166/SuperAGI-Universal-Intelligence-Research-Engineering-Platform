from __future__ import annotations
from ..models import SimulationResult, SpikeTrain
class MockNeuroAdapter:
    available=True
    def run_simulation(self, network, config):
        spikes=[SpikeTrain(neuron_id=n.id,timestamps=[config.timestep*10],duration=config.duration) for n in network.neurons]
        return SimulationResult(status="SIMULATION_RESULT",spikes=spikes,backend="mock",limitations=["Deterministic mock backend; not a biological simulation."])
class NeuroSimulationEngine:
    def __init__(self, adapters=None): self.adapters=adapters or {"mock":MockNeuroAdapter()}
    def run(self, network, config):
        adapter=self.adapters.get(config.backend)
        if adapter is None: return SimulationResult(status="UNAVAILABLE",backend=config.backend,limitations=["Requested backend is not configured; no backend was substituted."])
        if not getattr(adapter,"available",False): return SimulationResult(status="UNAVAILABLE",backend=config.backend,limitations=["Requested backend is unavailable."])
        result=adapter.run_simulation(network,config)
        return result if isinstance(result,SimulationResult) else SimulationResult(status=result.get("status","FAILED"),backend=config.backend,limitations=[result.get("error", "Backend failed")])
