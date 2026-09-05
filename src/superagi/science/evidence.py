from .models import KnowledgeItem, KnowledgeKind
def linked_evidence(statement, evidence_refs=(), provenance_refs=()): return KnowledgeItem(statement=statement, kind=KnowledgeKind.EVIDENCE, evidence_refs=list(evidence_refs), provenance_refs=list(provenance_refs))
