class QiskitAdapter:
 def __init__(self):
  try: import qiskit; self._module=qiskit
  except ImportError:self._module=None
 @property
 def available(self):return self._module is not None
