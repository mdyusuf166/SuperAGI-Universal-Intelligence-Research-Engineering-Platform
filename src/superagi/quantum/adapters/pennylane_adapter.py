from .qiskit_adapter import QiskitAdapter
class PennyLaneAdapter(QiskitAdapter):
 def __init__(self):
  try: import pennylane; self._module=pennylane
  except ImportError:self._module=None
