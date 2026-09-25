"""Demo D: two evidence values stay unresolved."""

from superagi.world_model import (
    EntityProperty,
    EntityStatus,
    EntityType,
    EpistemicStatus,
    KnowledgeGraph,
    PropertyValue,
    ResolutionStatus,
    WorldEntity,
    provenance_from,
)


def build():
    graph = KnowledgeGraph()
    sensor = graph.add_entity(
        WorldEntity(
            entity_type=EntityType.DEVICE,
            name="bench sensor",
            status=EntityStatus.PROPOSED,
            epistemic=EpistemicStatus.EVIDENCED,
            provenance=provenance_from("bench notes", agent="demo"),
            properties=[EntityProperty(name="temperature", value=PropertyValue(number=20), epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["note-20"], provenance=provenance_from("note-20"))],
        )
    )
    graph.update_entity(sensor.id, properties=[EntityProperty(name="temperature", value=PropertyValue(number=40), epistemic=EpistemicStatus.EVIDENCED, evidence_refs=["note-40"], provenance=provenance_from("note-40"))])
    conflict = graph.detect_contradictions()[0]
    untouched = graph.resolve_conflict(conflict.id, evidence_ref="missing-note", rule="not a supplied evidence ref")
    return {
        "banner": ["EVIDENCED", "CONTRADICTED", "UNRESOLVED"],
        "values": sorted(item.number for item in conflict.conflicting_values),
        "epistemic": sorted({prop.epistemic.value for prop in sensor.properties if prop.name == "temperature"}),
        "resolution": untouched.resolution_status.value,
        "selected": untouched.selected_evidence,
        "executed": False,
    }


def main():
    report = build()
    print("CONTRADICTED")
    print("UNRESOLVED")
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
