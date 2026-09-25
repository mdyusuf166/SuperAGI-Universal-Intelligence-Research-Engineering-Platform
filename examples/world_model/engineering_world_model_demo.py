"""Demo B: engineering system world model. Planning stays a proposal."""

from superagi.evolution.models import PlanningAction
from superagi.world_model import (
    EntityProperty,
    EntityStatus,
    EntityType,
    EpistemicStatus,
    KnowledgeGraph,
    PlanningAdapter,
    PropertyValue,
    RelationType,
    WorldConstraint,
    WorldEntity,
    WorldRelation,
    provenance_from,
)
from superagi.world_model.reasoning import BoundedReasoner


def build():
    graph = KnowledgeGraph()
    system = graph.add_entity(WorldEntity(entity_type=EntityType.SYSTEM, name="cooling loop", status=EntityStatus.OBSERVED, epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("declared schematic", agent="demo"), properties=[EntityProperty(name="power", value=PropertyValue(number=5), epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("declared schematic"))]))
    pump = graph.add_entity(WorldEntity(entity_type=EntityType.COMPONENT, name="pump", status=EntityStatus.OBSERVED, epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("declared schematic")))
    sensor = graph.add_entity(WorldEntity(entity_type=EntityType.DEVICE, name="sensor", status=EntityStatus.PROPOSED, epistemic=EpistemicStatus.UNKNOWN, provenance=provenance_from(None)))
    graph.add_relation(WorldRelation(source_id=pump.id, relation=RelationType.PART_OF, target_id=system.id, epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["declared schematic"], status="SUPPORTED", provenance=provenance_from("declared schematic")))
    graph.add_relation(WorldRelation(source_id=sensor.id, relation=RelationType.PART_OF, target_id=pump.id, epistemic=EpistemicStatus.EVIDENCED, provenance=provenance_from("declared schematic")))
    inferred = BoundedReasoner().infer_transitive(graph, RelationType.PART_OF)
    constraint = WorldConstraint(statement="Declared power stays at or below 6.", kind="max_number", limit=6, entity_id=system.id, property_name="power", provenance=provenance_from("declared schematic"))
    check = BoundedReasoner().check_constraints(graph, [constraint])
    planned = PlanningAdapter().evaluate(goal_statement="Review the cooling loop.", actions=[PlanningAction(name="review-loop", cost=1, risk=0, deltas=[], estimated_outcome="Review the declared schematic.")], variables=[("power", 5)], weights={"cost": 1}, outcome_variable="power")
    return {
        "banner": ["OBSERVED", "EVIDENCED", "INFERRED", "UNKNOWN", "PROPOSAL_ONLY"],
        "inferred": inferred[0].epistemic.value,
        "constraint": check[0].satisfied,
        "plan_status": planned["status"],
        "plan_executed": planned["executed"],
        "sensor": sensor.epistemic.value,
        "executed": False,
    }


def main():
    report = build()
    print("ENGINEERING WORLD MODEL")
    print("PROPOSAL ONLY")
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
