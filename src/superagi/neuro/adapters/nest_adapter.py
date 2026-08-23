from __future__ import annotations
class NestAdapter:
    def __init__(self):
        try: import nest as module; self._module=module
        except ImportError: self._module=None
    @property
    def available(self): return self._module is not None
    def create_neuron(self, *args, **kwargs): return {"status":"AVAILABLE"} if self.available else {"status":"UNAVAILABLE", "error":"NEST is unavailable"}
    create_network=create_neuron
    def run_simulation(self, *args, **kwargs): return {"status":"UNAVAILABLE", "error":"NEST is unavailable"} if not self.available else {"status":"FAILED", "error":"NEST simulation configuration not implemented"}
