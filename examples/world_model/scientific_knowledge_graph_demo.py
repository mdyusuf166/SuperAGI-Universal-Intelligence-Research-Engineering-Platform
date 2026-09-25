"""Demo A: scientific knowledge graph. Labels stay hypothesis, inference, and prediction."""

from superagi.science.hypothesis import HypothesisGenerator
from superagi.science.models import ScientificQuestion
from superagi.world_model import (
    BoundedReasoner,
    EntityProperty,
    EntityStatus,
    EntityType,
    EpistemicStatus,
    KnowledgeGraph,
    PropertyValue,
    RelationType,
    WorldEntity,
    WorldRelation,
    provenance_from,
)


def build():
    question = ScientificQuestion(question="How might a declared moisture reading relate to growth?", variables=["moisture"], evidence_refs=["user-supplied note"], assumptions=["The note was supplied by the user."])
    hypothesis = HypothesisGenerator().generate(question)
    graph = KnowledgeGraph()
    paper = graph.add_entity(WorldEntity(entity_type=EntityType.PAPER, name="moisture note", status=EntityStatus.OBSERVED, epistemic=EpistemicStatus.EVIDENCED, provenance=provenance_from("user-supplied note", agent="demo")))
    idea = graph.add_entity(WorldEntity(entity_type=EntityType.HYPOTHESIS, name=hypothesis.hypothesis[:80], status=EntityStatus.PROPOSED, epistemic=EpistemicStatus.HYPOTHESIZED, provenance=provenance_from("user-supplied note", agent="demo")))
    trial = graph.add_entity(WorldEntity(entity_type=EntityType.EXPERIMENT, name="non-executing moisture check", status=EntityStatus.PROPOSED, epistemic=EpistemicStatus.UNKNOWN, provenance=provenance_from(None)))
    molecule = graph.add_entity(WorldEntity(entity_type=EntityType.MOLECULE, name="marker", status=EntityStatus.PROPOSED, epistemic=EpistemicStatus.UNKNOWN, provenance=provenance_from(None)))
    cell = graph.add_entity(WorldEntity(entity_type=EntityType.CELL, name="sample cell", status=EntityStatus.PROPOSED, epistemic=EpistemicStatus.UNKNOWN, provenance=provenance_from(None)))
    system = graph.add_entity(WorldEntity(entity_type=EntityType.SYSTEM, name="sample culture", status=EntityStatus.PROPOSED, epistemic=EpistemicStatus.UNKNOWN, provenance=provenance_from(None)))
    graph.add_relation(WorldRelation(source_id=idea.id, relation=RelationType.SUPPORTS, target_id=paper.id, status="SUPPORTED", epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["user-supplied note"], provenance=provenance_from("user-supplied note")))
    causal = graph.add_relation(WorldRelation(source_id=idea.id, relation=RelationType.CAUSES_HYPOTHESIS, target_id=trial.id, epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("user-supplied note")))
    graph.add_relation(WorldRelation(source_id=molecule.id, relation=RelationType.PART_OF, target_id=cell.id, epistemic=EpistemicStatus.EVIDENCED, provenance=provenance_from("user-supplied note")))
    graph.add_relation(WorldRelation(source_id=cell.id, relation=RelationType.PART_OF, target_id=system.id, epistemic=EpistemicStatus.EVIDENCED, provenance=provenance_from("user-supplied note")))
    inferred = BoundedReasoner().infer_transitive(graph, RelationType.PART_OF)
    graph.update_entity(paper.id, properties=[EntityProperty(name="moisture", value=PropertyValue(number=3), epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("user-supplied note"))])
    return {
        "banner": ["OBSERVED", "EVIDENCED", "INFERRED", "HYPOTHESIZED", "UNKNOWN"],
        "hypothesis_status": hypothesis.status.value,
        "causal_epistemic": causal.epistemic.value,
        "causal_verification": causal.verification,
        "inferred": inferred[0].epistemic.value if inferred else "",
        "experiment": trial.epistemic.value,
        "executed": False,
    }


def main():
    report = build()
    print("KNOWLEDGE GRAPH")
    print("NOT A TRUTH GUARANTEE")
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
