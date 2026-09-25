"""Bounded graph reasoning. Derived rows are labeled INFERRED."""

from __future__ import annotations

from uuid import UUID

from .graph import KnowledgeGraph
from .models import (
    ConstraintCheck,
    EpistemicStatus,
    EvidenceAggregate,
    EvidenceLinkStatus,
    RelationType,
    StateDelta,
    WorldRelation,
    WorldState,
)
from .provenance import provenance_from
from .uncertainty import combine

_TRANSITIVE = {RelationType.PART_OF, RelationType.DEPENDS_ON, RelationType.PRECEDES}


class BoundedReasoner:
    def infer_transitive(self, graph: KnowledgeGraph, relation: RelationType) -> list[WorldRelation]:
        if relation not in _TRANSITIVE:
            raise ValueError(f"Transitive inference is not configured for {relation.value}")
        direct = {(item.source_id, item.target_id) for item in graph.get_relations(relation=relation)}
        created: list[WorldRelation] = []
        for entity in graph.entities():
            reached = self._reach(graph, entity.id, relation)
            for target_id, via in sorted(reached.items(), key=lambda item: (graph.get_entity(item[0]).name, str(item[0]))):
                if (entity.id, target_id) in direct or target_id == entity.id:
                    continue
                inferred = graph.add_relation(
                    WorldRelation(
                        source_id=entity.id,
                        relation=relation,
                        target_id=target_id,
                        epistemic=EpistemicStatus.INFERRED,
                        status=EvidenceLinkStatus.UNKNOWN,
                        basis=f"Transitive {relation.value} via {via}",
                        provenance=provenance_from(None, agent="bounded_reasoner"),
                    )
                )
                created.append(inferred)
                direct.add((entity.id, target_id))
        return created

    def compare_states(self, before: WorldState, after: WorldState) -> list[StateDelta]:
        left = {item.entity_id: item for item in before.entity_states}
        right = {item.entity_id: item for item in after.entity_states}
        deltas: list[StateDelta] = []
        for entity_id in sorted(set(left) | set(right), key=str):
            before_props = {prop.name: prop for prop in left.get(entity_id).properties} if entity_id in left else {}
            after_props = {prop.name: prop for prop in right.get(entity_id).properties} if entity_id in right else {}
            for name in sorted(set(before_props) | set(after_props)):
                earlier = before_props.get(name)
                later = after_props.get(name)
                deltas.append(
                    StateDelta(
                        name=name,
                        before=earlier.value if earlier else None,
                        after=later.value if later else None,
                        before_epistemic=earlier.epistemic if earlier else before.epistemic,
                        after_epistemic=later.epistemic if later else after.epistemic,
                    )
                )
        return deltas

    def check_constraints(self, graph: KnowledgeGraph, constraints: list) -> list[ConstraintCheck]:
        checks: list[ConstraintCheck] = []
        for constraint in constraints:
            if constraint.entity_id is None or constraint.property_name is None or constraint.limit is None:
                checks.append(ConstraintCheck(constraint_id=constraint.id, satisfied=False, detail="UNKNOWN. The constraint does not name an entity property and limit."))
                continue
            entity = graph.get_entity(constraint.entity_id)
            props = [item for item in entity.properties if item.name == constraint.property_name and item.value.number is not None and item.epistemic != EpistemicStatus.CONTRADICTED]
            if not props:
                checks.append(ConstraintCheck(constraint_id=constraint.id, satisfied=False, detail="UNKNOWN. No uncontested numeric property was recorded."))
                continue
            value = props[0].value.number or 0
            ok = value <= constraint.limit if constraint.kind == "max_number" else False
            detail = f"{constraint.property_name}={value} limit={constraint.limit}" if ok else f"{constraint.property_name}={value} exceeds {constraint.limit}"
            if constraint.kind != "max_number":
                detail = "UNKNOWN. Constraint kind is not configured."
            checks.append(ConstraintCheck(constraint_id=constraint.id, satisfied=ok, detail=detail))
        return checks

    def aggregate_evidence(self, relation: WorldRelation) -> EvidenceAggregate:
        if relation.status == EvidenceLinkStatus.CONTRADICTED or relation.relation == RelationType.CONTRADICTS:
            return EvidenceAggregate(status=EvidenceLinkStatus.CONTRADICTED, confidence=None, basis="Conflicting relation labels are kept. No winner was selected.", count=len(relation.evidence_refs))
        if not relation.evidence_refs:
            return EvidenceAggregate(status=EvidenceLinkStatus.UNKNOWN, confidence=None, basis="No evidence references were supplied.", count=0)
        report = combine([relation.confidence] if relation.confidence is not None else [])
        return EvidenceAggregate(status=relation.status, confidence=report.confidence, basis=report.basis, count=len(relation.evidence_refs))

    def _reach(self, graph: KnowledgeGraph, start: UUID, relation: RelationType) -> dict[UUID, str]:
        reached: dict[UUID, str] = {}
        queue = [(start, "")]
        seen = {start}
        while queue:
            current, trail = queue.pop(0)
            outs = [item for item in graph.get_relations(entity_id=current, relation=relation) if item.source_id == current]
            outs.sort(key=lambda item: (graph.get_entity(item.target_id).name, str(item.target_id)))
            for edge in outs:
                target = edge.target_id
                via = f"{trail}>{target}" if trail else str(target)
                if target in seen:
                    continue
                seen.add(target)
                if target != start:
                    reached[target] = via
                queue.append((target, via))
        return reached
