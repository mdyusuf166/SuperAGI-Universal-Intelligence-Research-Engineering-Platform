"""Demo C: robot grid walk recorded as a simulated world state."""

from superagi.robotics.planning.path_planner import AStarPlanner
from superagi.world_model import (
    EntityProperty,
    EntityStatus,
    EntityType,
    EpistemicStatus,
    KnowledgeGraph,
    PropertyValue,
    SimulationAdapter,
    Timeline,
    WorldEntity,
    WorldModelDomainRegistry,
    provenance_from,
)


def build():
    path = AStarPlanner().plan((0, 0), (2, 0))
    graph = KnowledgeGraph()
    robot = graph.add_entity(WorldEntity(entity_type=EntityType.ROBOT, name="grid robot", status=EntityStatus.OBSERVED, epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("declared start cell", agent="demo"), properties=[EntityProperty(name="x", value=PropertyValue(number=0), epistemic=EpistemicStatus.OBSERVED, provenance=provenance_from("declared start cell"))]))
    timeline = Timeline()
    linked = SimulationAdapter().run(graph, timeline, entity_id=robot.id, variables=[("x", path[0].x), ("y", path[0].y)], deltas=[("x", path[1].x - path[0].x), ("y", path[1].y - path[0].y)], source="declared start cell")
    simulated = graph.annotations_for(robot.id, EpistemicStatus.SIMULATED)
    unavailable = WorldModelDomainRegistry().adapter("robotics").import_backend()
    return {
        "banner": ["OBSERVED", "SIMULATED", "UNAVAILABLE"],
        "path": [{"x": point.x, "y": point.y} for point in path],
        "observed_x": robot.properties[0].value.number,
        "simulated_x": simulated[0].property.value.number,
        "simulated_epistemic": simulated[0].property.epistemic.value,
        "classification": linked.classification,
        "robotics_backend": unavailable.status,
        "executed": False,
    }


def main():
    report = build()
    print("SIMULATED")
    print("NOT OBSERVED")
    print("NO REAL-WORLD EXECUTION")
    for key, value in report.items():
        print(f"{key}: {value}")
    return report


if __name__ == "__main__":
    main()
