class CircuitValidator:
 def validate(self,circuit):
  ids=[c.identifier for c in circuit.components];issues=[]
  if len(ids)!=len(set(ids)):issues.append("duplicate identifiers")
  for c in circuit.components:
   if len(c.nodes)<2 or any(n not in circuit.nodes for n in c.nodes):issues.append(f"invalid nodes: {c.identifier}")
  return {"valid":not issues,"issues":issues}
