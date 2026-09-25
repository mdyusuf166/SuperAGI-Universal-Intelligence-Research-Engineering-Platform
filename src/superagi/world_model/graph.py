"""Deterministic typed knowledge graph."""

from __future__ import annotations

from uuid import UUID

from .models import (
    Annotation,
    Conflict,
    EntityProperty,
    EntityStatus,
    EpistemicStatus,
    EvidenceLinkStatus,
    PropertyValue,
    ProvenanceRef,
    RelationType,
    ResolutionStatus,
    ValidationIssue,
    WorldEntity,
    WorldEvent,
    WorldRelation,
    utc_now,
)
from .validation import WorldModelSafetyPolicy

_SELF_PROHIBITED = {
    RelationType.PART_OF,
    RelationType.CONTAINS,
    RelationType.CONNECTED_TO,
    RelationType.DEPENDS_ON,
    RelationType.CAUSES_HYPOTHESIS,
    RelationType.CORRELATED_WITH,
    RelationType.PRECEDES,
    RelationType.FOLLOWS,
    RelationType.LOCATED_IN,
    RelationType.USES,
    RelationType.PRODUCES,
    RelationType.REQUIRES,
    RelationType.CONTRADICTS,
    RelationType.SUPPORTS,
    RelationType.DERIVED_FROM,
}

_OPENING = {EpistemicStatus.OBSERVED, EpistemicStatus.EVIDENCED}
_FACTUAL = {EpistemicStatus.OBSERVED, EpistemicStatus.EVIDENCED, EpistemicStatus.CONTRADICTED}


class KnowledgeGraph:
    def __init__(self) -> None:
        self._entities: dict[UUID, WorldEntity] = {}
        self._name_index: dict[tuple[str, str], UUID] = {}
        self._relations: dict[UUID, WorldRelation] = {}
        self._relation_keys: set[tuple[UUID, RelationType, UUID]] = set()
        self._events: dict[UUID, WorldEvent] = {}
        self._annotations: list[Annotation] = []
        self._conflicts: dict[UUID, Conflict] = {}
        self._conflict_keys: set[tuple[str, str]] = set()
        self.safety = WorldModelSafetyPolicy()

    def add_entity(self, entity: WorldEntity) -> WorldEntity:
        self._guard_entity(entity)
        key = (entity.entity_type.value, entity.name.casefold())
        if key in self._name_index:
            raise ValueError(f"Duplicate entity: {entity.entity_type.value} {entity.name}")
        self._entities[entity.id] = entity
        self._name_index[key] = entity.id
        self._scan_properties(entity)
        return entity

    def get_entity(self, entity_id: UUID) -> WorldEntity:
        try:
            return self._entities[entity_id]
        except KeyError as exc:
            raise KeyError(f"Unknown entity: {entity_id}") from exc

    def get_by_name(self, name: str, entity_type: str | None = None) -> list[WorldEntity]:
        folded = name.casefold()
        found = [entity for entity in self.entities() if entity.name.casefold() == folded and (entity_type is None or entity.entity_type.value == entity_type)]
        return found

    def update_entity(self, entity_id: UUID, *, status: EntityStatus | None = None, properties: list[EntityProperty] | None = None) -> WorldEntity:
        entity = self.get_entity(entity_id)
        if status is not None:
            entity.status = status
            entity.updated_at = utc_now()
        for prop in properties or []:
            self.safety.guard(f"{prop.name} {prop.value.text or ''}")
            if prop.epistemic in {EpistemicStatus.PREDICTED, EpistemicStatus.SIMULATED, EpistemicStatus.INFERRED}:
                self.add_annotation(entity_id, prop)
                continue
            same = [item for item in entity.properties if item.name == prop.name and item.value.key() == prop.value.key()]
            if same:
                continue
            entity.properties.append(prop)
        self._scan_properties(entity)
        return entity

    def add_relation(self, relation: WorldRelation) -> WorldRelation:
        if not isinstance(relation.relation, RelationType):
            raise ValueError("Invalid relation type")
        self.safety.guard(relation.basis)
        if relation.source_id not in self._entities or relation.target_id not in self._entities:
            raise ValueError("Invalid entity reference")
        if relation.source_id == relation.target_id and relation.relation in _SELF_PROHIBITED:
            raise ValueError(f"Self-referential relation is prohibited: {relation.relation.value}")
        key = (relation.source_id, relation.relation, relation.target_id)
        if key in self._relation_keys:
            raise ValueError("Duplicate relation")
        stored = self._label_relation(relation)
        self._relations[stored.id] = stored
        self._relation_keys.add(key)
        self._scan_relation_conflicts()
        return stored

    def remove_relation(self, relation_id: UUID) -> WorldRelation:
        try:
            relation = self._relations.pop(relation_id)
        except KeyError as exc:
            raise KeyError(f"Unknown relation: {relation_id}") from exc
        self._relation_keys.discard((relation.source_id, relation.relation, relation.target_id))
        return relation

    def get_relations(self, *, entity_id: UUID | None = None, relation: RelationType | None = None) -> list[WorldRelation]:
        selected = list(self._relations.values())
        if entity_id is not None:
            selected = [item for item in selected if item.source_id == entity_id or item.target_id == entity_id]
        if relation is not None:
            selected = [item for item in selected if item.relation == relation]
        return sorted(selected, key=self._relation_sort)

    def neighbors(self, entity_id: UUID, *, direction: str = "out") -> list[WorldEntity]:
        self.get_entity(entity_id)
        ids: list[UUID] = []
        for relation in self._relations.values():
            if direction in {"out", "both"} and relation.source_id == entity_id:
                ids.append(relation.target_id)
            if direction in {"in", "both"} and relation.target_id == entity_id:
                ids.append(relation.source_id)
        unique = []
        seen: set[UUID] = set()
        for item_id in ids:
            if item_id not in seen and item_id != entity_id:
                seen.add(item_id)
                unique.append(self._entities[item_id])
        unique.sort(key=lambda entity: (entity.name, str(entity.id)))
        return unique

    def path(self, source_id: UUID, target_id: UUID) -> list[UUID]:
        self.get_entity(source_id)
        self.get_entity(target_id)
        if source_id == target_id:
            return [source_id]
        previous: dict[UUID, UUID | None] = {source_id: None}
        queue = [source_id]
        while queue:
            current = queue.pop(0)
            for nxt in self.neighbors(current, direction="out"):
                if nxt.id in previous:
                    continue
                previous[nxt.id] = current
                if nxt.id == target_id:
                    chain = [target_id]
                    while chain[-1] != source_id:
                        parent = previous[chain[-1]]
                        if parent is None:
                            break
                        chain.append(parent)
                    return list(reversed(chain))
                queue.append(nxt.id)
        return []

    def subgraph(self, entity_ids: list[UUID]) -> "KnowledgeGraph":
        selected = set(entity_ids)
        for entity_id in selected:
            self.get_entity(entity_id)
        child = KnowledgeGraph()
        ordered = sorted(selected, key=lambda item: (self._entities[item].name, str(item)))
        for entity_id in ordered:
            child.add_entity(self._entities[entity_id].model_copy(deep=True))
        for relation in self.get_relations():
            if relation.source_id in selected and relation.target_id in selected:
                child.add_relation(relation.model_copy(deep=True))
        return child

    def add_event(self, event: WorldEvent) -> WorldEvent:
        self.safety.guard(event.name)
        for entity_id in event.entity_ids:
            self.get_entity(entity_id)
        self._events[event.id] = event
        return event

    def events_for(self, entity_id: UUID) -> list[WorldEvent]:
        self.get_entity(entity_id)
        selected = [event for event in self._events.values() if entity_id in event.entity_ids]
        return sorted(selected, key=lambda event: (event.time.step, event.name, str(event.id)))

    def add_annotation(self, entity_id: UUID, prop: EntityProperty) -> Annotation:
        self.get_entity(entity_id)
        if prop.epistemic not in {EpistemicStatus.PREDICTED, EpistemicStatus.SIMULATED, EpistemicStatus.INFERRED, EpistemicStatus.HYPOTHESIZED}:
            prop = prop.model_copy(update={"epistemic": EpistemicStatus.INFERRED})
        note = Annotation(entity_id=entity_id, property=prop)
        self._annotations.append(note)
        return note

    def annotations_for(self, entity_id: UUID, epistemic: EpistemicStatus | None = None) -> list[Annotation]:
        selected = [item for item in self._annotations if item.entity_id == entity_id and (epistemic is None or item.property.epistemic == epistemic)]
        return sorted(selected, key=lambda item: (item.property.name, item.property.epistemic.value, str(item.id)))

    def entities(self) -> list[WorldEntity]:
        return sorted(self._entities.values(), key=lambda entity: (entity.name, str(entity.id)))

    def conflicts(self) -> list[Conflict]:
        return sorted(self._conflicts.values(), key=lambda item: (item.subject, str(item.entity_id), str(item.id)))

    def detect_contradictions(self) -> list[Conflict]:
        for entity in self.entities():
            self._scan_properties(entity)
        self._scan_relation_conflicts()
        return self.conflicts()

    def resolve_conflict(self, conflict_id: UUID, *, evidence_ref: str, rule: str) -> Conflict:
        try:
            conflict = self._conflicts[conflict_id]
        except KeyError as exc:
            raise KeyError(f"Unknown conflict: {conflict_id}") from exc
        if not rule or evidence_ref not in conflict.evidence_refs:
            return conflict
        conflict.resolution_status = ResolutionStatus.RESOLVED
        conflict.resolution_rule = rule
        conflict.selected_evidence = evidence_ref
        return conflict

    def validate(self) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        seen: dict[tuple[str, str], UUID] = {}
        for entity in self.entities():
            key = (entity.entity_type.value, entity.name.casefold())
            if key in seen:
                issues.append(ValidationIssue(code="duplicate_entity", message=f"Duplicate entity {entity.name}"))
            seen[key] = entity.id
            if entity.epistemic == EpistemicStatus.OBSERVED and entity.provenance.status.value == "MISSING":
                issues.append(ValidationIssue(code="missing_provenance", message=f"Observed entity {entity.name} has no source"))
        relation_seen: set[tuple[UUID, RelationType, UUID]] = set()
        for relation in self.get_relations():
            if relation.source_id not in self._entities or relation.target_id not in self._entities:
                issues.append(ValidationIssue(code="invalid_reference", message="Relation endpoint is missing"))
            if relation.source_id == relation.target_id and relation.relation in _SELF_PROHIBITED:
                issues.append(ValidationIssue(code="self_relation", message=relation.relation.value))
            key = (relation.source_id, relation.relation, relation.target_id)
            if key in relation_seen:
                issues.append(ValidationIssue(code="duplicate_relation", message=relation.relation.value))
            relation_seen.add(key)
            if relation.relation == RelationType.CAUSES_HYPOTHESIS and relation.verification != "NOT CAUSALLY VERIFIED":
                issues.append(ValidationIssue(code="causal_overclaim", message="CAUSES_HYPOTHESIS is not verified causation"))
            if relation.relation == RelationType.CAUSES_HYPOTHESIS and relation.epistemic != EpistemicStatus.HYPOTHESIZED:
                issues.append(ValidationIssue(code="causal_overclaim", message="CAUSES_HYPOTHESIS must stay HYPOTHESIZED"))
        return issues

    def _guard_entity(self, entity: WorldEntity) -> None:
        chunks = [entity.name]
        for prop in entity.properties:
            chunks.append(prop.name)
            if prop.value.text:
                chunks.append(prop.value.text)
        self.safety.guard(" ".join(chunks))

    def _scan_properties(self, entity: WorldEntity) -> None:
        grouped: dict[str, list[EntityProperty]] = {}
        for prop in entity.properties:
            grouped.setdefault(prop.name, []).append(prop)
        for name, props in grouped.items():
            keys = {prop.value.key() for prop in props}
            factual = [prop for prop in props if prop.epistemic in _FACTUAL]
            if len(keys) < 2 or len(factual) < 2:
                continue
            for prop in factual:
                if prop.epistemic in _OPENING:
                    prop.epistemic = EpistemicStatus.CONTRADICTED
                    prop.status = EvidenceLinkStatus.CONTRADICTED
            conflict_key = (str(entity.id), name)
            if conflict_key in self._conflict_keys:
                continue
            values = []
            evidence: list[str] = []
            provenance: list[ProvenanceRef] = []
            for prop in factual:
                values.append(prop.value)
                evidence.extend(prop.evidence_refs)
                provenance.append(prop.provenance)
            conflict = Conflict(entity_id=entity.id, subject=name, conflicting_values=values, evidence_refs=_unique(evidence), provenance=provenance)
            self._conflicts[conflict.id] = conflict
            self._conflict_keys.add(conflict_key)

    def _scan_relation_conflicts(self) -> None:
        groups: dict[tuple[UUID, UUID], list[WorldRelation]] = {}
        for relation in self._relations.values():
            pair = (relation.source_id, relation.target_id)
            groups.setdefault(pair, []).append(relation)
        for (source_id, target_id), relations in groups.items():
            kinds = {item.relation for item in relations}
            if RelationType.SUPPORTS not in kinds or RelationType.CONTRADICTS not in kinds:
                continue
            conflict_key = (f"{source_id}:{target_id}", "SUPPORTS/CONTRADICTS")
            if conflict_key in self._conflict_keys:
                continue
            evidence: list[str] = []
            provenance: list[ProvenanceRef] = []
            for relation in relations:
                if relation.relation in {RelationType.SUPPORTS, RelationType.CONTRADICTS}:
                    evidence.extend(relation.evidence_refs)
                    provenance.append(relation.provenance)
            conflict = Conflict(
                entity_id=source_id,
                subject="SUPPORTS/CONTRADICTS",
                conflicting_values=[PropertyValue(text="SUPPORTS"), PropertyValue(text="CONTRADICTS")],
                evidence_refs=_unique(evidence),
                provenance=provenance,
            )
            self._conflicts[conflict.id] = conflict
            self._conflict_keys.add(conflict_key)

    def _label_relation(self, relation: WorldRelation) -> WorldRelation:
        if relation.relation == RelationType.CAUSES_HYPOTHESIS:
            return relation.model_copy(update={"epistemic": EpistemicStatus.HYPOTHESIZED, "status": EvidenceLinkStatus.UNKNOWN, "causal_status": "CAUSAL HYPOTHESIS", "verification": "NOT CAUSALLY VERIFIED", "basis": relation.basis or "Declared causal hypothesis. Not causal proof."})
        if relation.relation == RelationType.CORRELATED_WITH:
            return relation.model_copy(update={"causal_status": "CORRELATION", "verification": "NOT CAUSATION", "basis": relation.basis or "Declared correlation. Not causation."})
        return relation

    def _relation_sort(self, relation: WorldRelation) -> tuple[str, str, str, str]:
        source = self._entities[relation.source_id].name
        target = self._entities[relation.target_id].name
        return (relation.relation.value, source, target, str(relation.id))


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
