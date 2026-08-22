from __future__ import annotations

import re
from uuid import UUID

from .entities import Entity
from .relations import Relation


class KnowledgeBase:
    def __init__(self) -> None:
        self._entities: dict[UUID, Entity] = {}
        self._relations: dict[UUID, Relation] = {}

    def add_entity(self, entity: Entity) -> Entity:
        self._entities[entity.id] = entity
        return entity

    def get_entity(self, entity_id: UUID) -> Entity | None:
        return self._entities.get(entity_id)

    def add_relation(self, relation: Relation) -> Relation:
        if relation.source_entity_id not in self._entities or relation.target_entity_id not in self._entities:
            raise ValueError("Both relation entities must be present")
        self._relations[relation.id] = relation
        return relation

    def get_relations(self, entity_id: UUID | None = None) -> list[Relation]:
        if entity_id is None:
            return list(self._relations.values())
        return [relation for relation in self._relations.values() if relation.source_entity_id == entity_id or relation.target_entity_id == entity_id]

    def find_related(self, entity_id: UUID) -> list[Entity]:
        ids = {relation.target_entity_id if relation.source_entity_id == entity_id else relation.source_entity_id for relation in self.get_relations(entity_id)}
        return [self._entities[item_id] for item_id in ids if item_id in self._entities]

    def search_entities(self, query: str) -> list[Entity]:
        terms = set(re.findall(r"[\w-]+", query.casefold()))
        return [entity for entity in self._entities.values() if terms & set(re.findall(r"[\w-]+", f"{entity.name} {entity.description}".casefold()))]
