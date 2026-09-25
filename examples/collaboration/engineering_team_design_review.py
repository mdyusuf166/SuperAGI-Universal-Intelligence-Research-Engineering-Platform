"""Demo C: engineering team design review. Conceptual and simulation-only."""

from superagi.collaboration import Consent, ConsentState, InteractionMode, RoleAssigner, CollaborationPipeline, register_collaboration_agents
from superagi.core.agents import AgentRegistry
from superagi.engineering import EngineeringConstraint, EngineeringPipeline, EngineeringRequirement, register_engineering_agents
from superagi.orchestration import AgentCapabilityRegistry


def build():
    objective = "Review a conceptual simulated environmental monitor."
    roles = [
        RoleAssigner().assign("engineering lead", "decision maker", ["Accept or reject the draft"], human=True),
        RoleAssigner().assign("systems agent", "systems", ["Draft the architecture"]),
        RoleAssigner().assign("circuit agent", "circuit", ["Draft a conceptual circuit note"]),
        RoleAssigner().assign("review agent", "review", ["Record open issues"]),
    ]
    agents = AgentRegistry()
    registry = AgentCapabilityRegistry()
    register_collaboration_agents(agents, registry)
    register_engineering_agents(agents, registry)
    engineering = EngineeringPipeline().run(objective, [EngineeringRequirement(statement="Describe a conceptual monitor.", verification_method="review")], [EngineeringConstraint(kind="execution", limit="simulation-only")])
    result = CollaborationPipeline().run(
        objective,
        participants=["engineering lead", "systems agent", "circuit agent", "review agent"],
        roles=roles,
        consent=Consent(state=ConsentState.GRANTED, scope=["session"], persistent=False),
        mode=InteractionMode.SIMULATION_ONLY,
        goal_statements=["Produce a conceptual design review."],
        task_specs=[
            {"title": "Draft the system sketch", "owner": "systems agent", "evidence": ["conceptual requirement"], "completion_criteria": ["Architecture is labeled conceptual"]},
            {"title": "Draft the circuit note", "owner": "circuit agent", "depends_on": ["Draft the system sketch"], "evidence": ["conceptual requirement"], "completion_criteria": ["No physical execution"]},
            {"title": "Review the draft", "owner": "review agent", "depends_on": ["Draft the circuit note"], "evidence": ["conceptual requirement"], "completion_criteria": ["Open issues stay visible"]},
        ],
        evidence=("conceptual requirement",),
        sources=("conceptual requirement",),
        registry=registry,
        capabilities=("engineering", "collaboration"),
    )
    return {
        "classification": ["ASSISTANCE_ONLY", engineering["classification"]],
        "status": result["status"],
        "engineering_status": engineering["status"],
        "executed": result["executed"],
        "engineering_executed": False,
        "roles": [role.name for role in roles],
        "tasks": [task.title for task in result["tasks"]],
        "review": result["review"]["accepted"],
        "engineering_review": engineering["review"].accepted,
        "report": result["report"],
        "engineering_report": engineering["report"],
        "winner": result["coordination"]["selected_conflict_winner"],
    }


def main():
    report = build()
    print("CONCEPTUAL / SIMULATION-ONLY")
    print("NO PHYSICAL EXECUTION")
    for key in ("status", "engineering_status", "roles", "tasks", "review", "engineering_review", "report", "engineering_report"):
        print(f"{key}: {report[key]}")
    return report


if __name__ == "__main__":
    main()
