"""Demo C: conceptual research robot. SIMULATION ONLY. CONCEPTUAL RESEARCH SYSTEM."""

from superagi.core.agents import AgentRegistry
from superagi.engineering import EngineeringConstraint, EngineeringPipeline, EngineeringRequirement, register_engineering_agents
from superagi.memory import UniversalMemory
from superagi.orchestration import AgentCapability, AgentCapabilityRegistry, AgentDescriptor
from superagi.robotics import AStarPlanner, Robot, RobotCommand
from superagi.robotics.safety.policies import RoboticsSafetyPolicy
from superagi.science.experiment import ExperimentDesigner
from superagi.science.integration import science_agent_descriptor
from superagi.science.models import ScientificQuestion

FLOW = [
    "research_objective",
    "requirements",
    "robot_architecture",
    "sensors",
    "navigation",
    "experiment_proposal",
    "simulation",
    "verification",
    "design_review",
    "engineering_report",
]


def build():
    objective = "Propose a simulated soil-moisture observation along a grid path."
    requirement = EngineeringRequirement(statement="Follow a simulated path and record a proposed moisture observation.", verification_method="simulation")
    constraint = EngineeringConstraint(kind="execution", limit="simulation-only")
    memory = UniversalMemory()
    pipeline = EngineeringPipeline(memory=memory)
    engineered = pipeline.run("Design a conceptual simulated research rover for a non-executing observation proposal.", [requirement], [constraint])
    robot = Robot(name="conceptual-research-rover", robot_type="mobile", sensors=["moisture", "imu"], actuators=["simulated-wheel"], capabilities=["simulation"])
    path = AStarPlanner().plan((0, 0), (3, 1))
    question = ScientificQuestion(question=objective, domain=["Robotics"], variables=["moisture"], provenance_refs=["arc12-conceptual-demo"])
    experiment = ExperimentDesigner().design(question)
    physical = RoboticsSafetyPolicy().assess(RobotCommand(command_type="deploy", parameters={"request": "autonomous physical deployment"}, requires_approval=True), approved=False)
    registry = AgentCapabilityRegistry()
    register_engineering_agents(AgentRegistry(), registry)
    registry.register(science_agent_descriptor())
    registry.register(AgentDescriptor(name="robotics_simulation_boundary", capability=AgentCapability(domain="robotics", capabilities=["robotics", "navigation"], task_types=["simulation"], safety_level="low")))
    return {
        "classification": ["SIMULATION ONLY", "CONCEPTUAL RESEARCH SYSTEM"],
        "flow": list(FLOW),
        "research_objective": objective,
        "requirements": [requirement.statement],
        "robot_architecture": {"name": robot.name, "robot_type": robot.robot_type, "capabilities": robot.capabilities},
        "sensors": list(robot.sensors),
        "navigation": [{"x": point.x, "y": point.y} for point in path],
        "experiment_proposal": {"objective": experiment.objective, "reproducibility": experiment.reproducibility, "risks": experiment.risks},
        "simulation": {"status": engineered["simulation"].status, "is_simulation": True, "control": engineered["control_proposal"].classification},
        "verification": engineered["verification"].status,
        "design_review": {"status": engineered["review"].status, "accepted": engineered["review"].accepted},
        "engineering_report": engineered["report"],
        "pipeline_status": engineered["status"],
        "orchestration": {
            "engineering": len(registry.discover(["engineering"], domain="engineering", safety_level="low")),
            "science": len(registry.discover(["science"], domain="science", safety_level="low")),
            "robotics": len(registry.discover(["navigation"], domain="robotics", safety_level="low")),
        },
        "safety": {"physical_command_allowed": physical.allowed, "mode": physical.mode, "command_sent": False},
        "provenance": list(engineered["design"].provenance),
        "arc07": "simulation-first robotics boundary",
        "arc09": "existing capability registry",
        "arc12": "non-executing experiment proposal",
    }


def main():
    report = build()
    print("SIMULATION ONLY")
    print("CONCEPTUAL RESEARCH SYSTEM")
    for key in ("flow", "research_objective", "requirements", "robot_architecture", "sensors", "navigation", "experiment_proposal", "simulation", "verification", "design_review", "engineering_report", "orchestration", "safety", "provenance"):
        print(f"{key}: {report[key]}")
    return report


if __name__ == "__main__":
    main()
