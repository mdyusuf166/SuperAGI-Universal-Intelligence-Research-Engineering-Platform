"""Deterministic queries over a world model."""

from __future__ import annotations

from uuid import UUID

from .graph import KnowledgeGraph
from .models import EpistemicStatus, EvidenceLinkStatus, PropertyValue, QueryHit, RelationType
from .temporal import Timeline


class WorldQuery:
    def __init__(self, graph: KnowledgeGraph, timeline: Timeline | None = None) -> None:
        self.graph = graph
        self.timeline = timeline or Timeline()

    def find_entity(self, name: str) -> list[QueryHit]:
        return [self._entity_hit(entity) for entity in self.graph.get_by_name(name)]

    def find_neighbors(self, entity_id: UUID) -> list[QueryHit]:
        return [self._entity_hit(entity) for entity in self.graph.neighbors(entity_id, direction="both")]

    def find_relation(self, relation: RelationType) -> list[QueryHit]:
        hits = []
        for item in self.graph.get_relations(relation=relation):
            source = self.graph.get_entity(item.source_id).name
            target = self.graph.get_entity(item.target_id).name
            hits.append(QueryHit(kind="relation", label=f"{source} {item.relation.value} {target}", epistemic=item.epistemic, ref_id=str(item.id)))
        return hits

    def find_path(self, source_id: UUID, target_id: UUID) -> list[str]:
        return [self.graph.get_entity(entity_id).name for entity_id in self.graph.path(source_id, target_id)]

    def find_by_type(self, entity_type: str) -> list[QueryHit]:
        selected = [entity for entity in self.graph.entities() if entity.entity_type.value == entity_type]
        return [self._entity_hit(entity) for entity in selected]

    def find_by_property(self, name: str, value: PropertyValue) -> list[QueryHit]:
        hits = []
        for entity in self.graph.entities():
            for prop in entity.properties:
                if prop.name == name and prop.value.key() == value.key() and prop.epistemic != EpistemicStatus.CONTRADICTED:
                    hits.append(QueryHit(kind="property", label=f"{entity.name}.{name}", epistemic=prop.epistemic, ref_id=str(entity.id)))
        return hits

    def find_events(self, entity_id: UUID) -> list[QueryHit]:
        return [QueryHit(kind="event", label=event.name, epistemic=event.epistemic, ref_id=str(event.id)) for event in self.graph.events_for(entity_id)]

    def find_state_at(self, step: int) -> QueryHit | None:
        snapshot = self.timeline.state_at(step)
        if snapshot is None:
            return None
        return QueryHit(kind="snapshot", label=snapshot.state.label, epistemic=snapshot.epistemic, ref_id=str(snapshot.id))

    def find_supporting_evidence(self, relation_id: UUID) -> list[str]:
        for relation in self.graph.get_relations():
            if relation.id == relation_id and relation.status == EvidenceLinkStatus.SUPPORTED:
                return list(relation.evidence_refs)
        return []

    def find_contradictions(self) -> list[QueryHit]:
        return [QueryHit(kind="conflict", label=item.subject, epistemic=EpistemicStatus.CONTRADICTED, ref_id=str(item.id)) for item in self.graph.detect_contradictions()]

    def find_provenance_chain(self, entity_id: UUID) -> list:
        entity = self.graph.get_entity(entity_id)
        chain = [entity.provenance]
        for relation in self.graph.get_relations(entity_id=entity_id):
            chain.append(relation.provenance)
        return chain

    def _entity_hit(self, entity) -> QueryHit:
        return QueryHit(kind="entity", label=entity.name, epistemic=entity.epistemic, ref_id=str(entity.id))
