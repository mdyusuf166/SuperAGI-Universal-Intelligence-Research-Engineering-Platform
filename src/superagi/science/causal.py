from .models import Cause,Effect,Mechanism,Relationship,RelationshipKind
class CausalGraph:
 def __init__(self): self.edges=[];self.relationships=[]
 def add(self,cause,effect,relationship="causal hypothesis",evidence_refs=(),mechanism=None):
  kind=RelationshipKind(relationship); item=Relationship(cause=Cause(name=cause),effect=Effect(name=effect),kind=kind,evidence_refs=list(evidence_refs),mechanism=Mechanism(description=mechanism,evidence_refs=list(evidence_refs)) if mechanism else None);self.relationships.append(item);self.edges.append({"cause":cause,"effect":effect,"relationship":kind.value,"evidence_refs":list(evidence_refs)});return item
 def paths(self,start): return [[e["cause"],e["effect"]] for e in self.edges if e["cause"]==start]
