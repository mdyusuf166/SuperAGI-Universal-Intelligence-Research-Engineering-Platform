from .qiskit_adapter import QiskitAdapter
class QiskitAerAdapter(QiskitAdapter):
 def __init__(self):
  try: import qiskit_aer; self._module=qiskit_aer
  except ImportError:self._module=None
