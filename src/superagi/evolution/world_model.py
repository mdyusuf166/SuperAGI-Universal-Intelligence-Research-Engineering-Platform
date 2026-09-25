"""Minimal world model stored through ARC-02 when a source is supplied."""

from __future__ import annotations

from .models import ProvenanceLink, WorldConstraint, WorldEntity, WorldEvent, WorldObservation, WorldRelation


class WorldModel:
    def __init__(self) -> None:
        self.entities: list[WorldEntity] = []
        self.relations: list[WorldRelation] = []
        self.constraints: list[WorldConstraint] = []
        self.observations: list[WorldObservation] = []
        self.events: list[WorldEvent] = []
        self.provenance: ProvenanceLink | None = None

    def add_entity(self, entity: WorldEntity) -> WorldEntity:
        self.entities.append(entity)
        return entity

    def add_relation(self, relation: WorldRelation) -> WorldRelation:
        self.relations.append(relation)
        return relation

    def summary(self) -> str:
        names = ", ".join(entity.name for entity in self.entities) or "none"
        return f"World model entities: {names}."

    def remember(self, memory, source: str | None) -> dict:
        if not source:
            self.provenance = ProvenanceLink(source=None, agent="world_model", missing=True)
            return {"stored": False, "reason": "missing provenance"}
        record = memory.remember(self.summary(), source=source, tags=("evolution", "world-model"))
        self.provenance = ProvenanceLink(source=source, agent="world_model", missing=False)
        if memory is not None:
            from .provenance import ProvenanceLog
            ProvenanceLog().record(source=source, agent="world_model", evidence=[self.summary()], memory=memory)
        return {"stored": True, "id": str(record.id)}
