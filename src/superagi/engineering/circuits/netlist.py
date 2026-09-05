from .circuit import Circuit
class Netlist:
 def __init__(self,circuit:Circuit):self.entries=[f"{c.identifier} {c.kind} {' '.join(c.nodes)}" for c in circuit.components]
