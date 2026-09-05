from .models import KnowledgeItem, KnowledgeKind, ScientificQuestion
class KnowledgeSynthesizer:
    def __init__(self, memory=None): self.memory=memory
    def synthesize(self,q: ScientificQuestion):
        items=[KnowledgeItem(statement=x,kind=KnowledgeKind.FACT,provenance_refs=q.provenance_refs) for x in q.known_facts]+[KnowledgeItem(statement=x,kind=KnowledgeKind.EVIDENCE,evidence_refs=q.evidence_refs,provenance_refs=q.provenance_refs) for x in q.evidence_refs]+[KnowledgeItem(statement=x,kind=KnowledgeKind.UNKNOWN,provenance_refs=q.provenance_refs) for x in q.unknowns]
        return {"items":items,"facts":q.known_facts,"evidence":q.evidence_refs,"unknowns":q.unknowns,"classification":"EVIDENCE" if q.evidence_refs else "UNKNOWN"}
