"""Bounded context. The cycle does not copy a whole memory store or graph."""

from __future__ import annotations

from .models import CognitiveContext, ContextItem, EpistemicStatus
from .perception import note_for

MAX_CONTEXT_ITEMS = 4


class CognitiveContextBuilder:
    def build(self, *, goal: str, observations, memory=None, graph=None, constraints: list[str] | None = None, research_notes: list[str] | None = None, source: str | None = None, personal_goal: str | None = None) -> CognitiveContext:
        truncated = False
        memories = self._memories(memory, goal, source)
        evidence = []
        for observation in observations:
            if observation.epistemic in {EpistemicStatus.EVIDENCED, EpistemicStatus.OBSERVED, EpistemicStatus.CONTRADICTED}:
                evidence.append(ContextItem(kind="evidence", label=observation.statement[:160], epistemic=observation.epistemic, ref_id=str(observation.id), provenance=observation.provenance))
        evidence, cut = self._bound(evidence)
        truncated = truncated or cut
        entities, relations = self._graph(graph, source)
        entities, cut = self._bound(entities)
        truncated = truncated or cut
        relations, cut = self._bound(relations)
        truncated = truncated or cut
        goals = []
        if personal_goal:
            goals.append(ContextItem(kind="goal", label=personal_goal[:160], epistemic=EpistemicStatus.UNKNOWN, provenance=note_for(source)))
        goals.append(ContextItem(kind="goal", label=goal[:160], epistemic=EpistemicStatus.UNKNOWN, provenance=note_for(source)))
        goals, cut = self._bound(goals)
        truncated = truncated or cut
        constraint_items = [ContextItem(kind="constraint", label=item[:160], epistemic=EpistemicStatus.UNKNOWN, provenance=note_for(source)) for item in constraints or []]
        constraint_items, cut = self._bound(constraint_items)
        truncated = truncated or cut
        notes = [ContextItem(kind="research", label=item[:160], epistemic=EpistemicStatus.HYPOTHESIZED, provenance=note_for(source)) for item in research_notes or []]
        notes, cut = self._bound(notes)
        truncated = truncated or cut
        memories, cut = self._bound(memories)
        truncated = truncated or cut
        return CognitiveContext(memories=memories, evidence=evidence, entities=entities, relations=relations, goals=goals, constraints=constraint_items, research_notes=notes, bound=MAX_CONTEXT_ITEMS, truncated=truncated, limitations=[f"At most {MAX_CONTEXT_ITEMS} items are kept in each context list."])

    def _memories(self, memory, goal: str, source: str | None) -> list[ContextItem]:
        if memory is None:
            return []
        items = []
        for result in memory.search(goal)[: MAX_CONTEXT_ITEMS + 1]:
            content = getattr(result.item, "content", "")
            items.append(ContextItem(kind="memory", label=str(content)[:160], epistemic=EpistemicStatus.EVIDENCED, ref_id=str(getattr(result.item, "id", "")), provenance=note_for(getattr(result.item, "source", None) or source, str(getattr(result.item, "id", "")))))
        return items

    def _graph(self, graph, source: str | None) -> tuple[list[ContextItem], list[ContextItem]]:
        if graph is None:
            return [], []
        entities = [ContextItem(kind="entity", label=entity.name, epistemic=self._map(entity.epistemic.value), ref_id=str(entity.id), provenance=note_for(entity.provenance.source, str(entity.id))) for entity in graph.entities()]
        relations = []
        for relation in graph.get_relations():
            source_name = graph.get_entity(relation.source_id).name
            target_name = graph.get_entity(relation.target_id).name
            relations.append(ContextItem(kind="relation", label=f"{source_name} {relation.relation.value} {target_name}", epistemic=self._map(relation.epistemic.value), ref_id=str(relation.id), provenance=note_for(relation.provenance.source, str(relation.id))))
        return entities, relations

    def _map(self, value: str) -> EpistemicStatus:
        try:
            return EpistemicStatus(value)
        except ValueError:
            return EpistemicStatus.UNKNOWN

    def _bound(self, items: list[ContextItem]) -> tuple[list[ContextItem], bool]:
        if len(items) <= MAX_CONTEXT_ITEMS:
            return items, False
        return items[:MAX_CONTEXT_ITEMS], True
