"""Demo A: research team collaboration. Proposals stay non-executing."""

from superagi.collaboration import (
    Consent,
    ConsentState,
    InteractionMode,
    RoleAssigner,
    CollaborationPipeline,
    register_collaboration_agents,
)
from superagi.core.agents import AgentRegistry
from superagi.orchestration import AgentCapabilityRegistry
from superagi.science.experiment import ExperimentDesigner
from superagi.science.hypothesis import HypothesisGenerator
from superagi.science.integration import science_agent_descriptor
from superagi.science.models import KnowledgeKind, ScientificQuestion


def build():
    objective = "Review a user-supplied note about soil moisture and draft a non-executing hypothesis."
    consent = Consent(state=ConsentState.GRANTED, scope=["session"], persistent=False)
    roles = [
        RoleAssigner().assign("research lead", "decision maker", ["Set the objective"], human=True),
        RoleAssigner().assign("research agent", "research", ["Draft a hypothesis"]),
        RoleAssigner().assign("evidence agent", "evidence", ["Cite only supplied evidence"]),
        RoleAssigner().assign("critic agent", "critic", ["State that the hypothesis is unproven"]),
    ]
    registry = AgentCapabilityRegistry()
    register_collaboration_agents(AgentRegistry(), registry)
    registry.register(science_agent_descriptor())
    question = ScientificQuestion(question=objective, variables=["soil moisture"], evidence_refs=["user-supplied field note"], assumptions=["The note was supplied by the user."])
    hypothesis = HypothesisGenerator().generate(question)
    experiment = ExperimentDesigner().design(question)
    result = CollaborationPipeline().run(
        objective,
        participants=["research lead", "research agent", "evidence agent", "critic agent"],
        roles=roles,
        consent=consent,
        mode=InteractionMode.AI_ASSISTED,
        goal_statements=["Produce a reviewed, non-executing research proposal."],
        task_specs=[
            {"title": "Collect the supplied note", "owner": "evidence agent", "evidence": ["user-supplied field note"], "completion_criteria": ["Note is cited"]},
            {"title": "Draft a hypothesis", "owner": "research agent", "depends_on": ["Collect the supplied note"], "evidence": ["user-supplied field note"], "completion_criteria": ["Hypothesis is labeled PROPOSED"]},
            {"title": "Critique the draft", "owner": "critic agent", "depends_on": ["Draft a hypothesis"], "evidence": ["user-supplied field note"], "completion_criteria": ["Unproven status is stated"]},
        ],
        evidence=("user-supplied field note",),
        sources=("user-supplied field note",),
        registry=registry,
        capabilities=("collaboration", "science"),
    )
    return {
        "classification": "ASSISTANCE_ONLY",
        "status": result["status"],
        "executed": result["executed"],
        "roles": [role.name for role in roles],
        "tasks": [task.title for task in result["tasks"]],
        "evidence": result["evidence"],
        "hypothesis": hypothesis.hypothesis,
        "hypothesis_status": hypothesis.status.value,
        "experiment": experiment.reproducibility,
        "knowledge": {
            KnowledgeKind.FACT.value: [],
            KnowledgeKind.EVIDENCE.value: ["user-supplied field note"],
            KnowledgeKind.INFERENCE.value: [],
            KnowledgeKind.HYPOTHESIS.value: [hypothesis.hypothesis],
            KnowledgeKind.UNKNOWN.value: ["No laboratory result was produced."],
            KnowledgeKind.CONTRADICTION.value: [],
        },
        "review": result["review"]["status"],
        "accepted": result["review"]["accepted"],
        "recommendation_status": result["recommendation"].status.value,
        "decision_status": result["decision"].status,
        "report": result["report"],
        "winner": result["coordination"]["selected_conflict_winner"],
    }


def main():
    report = build()
    print("ASSISTANCE_ONLY")
    print("NON-EXECUTING RESEARCH COLLABORATION")
    for key in ("status", "roles", "tasks", "evidence", "hypothesis", "hypothesis_status", "experiment", "knowledge", "review", "report"):
        print(f"{key}: {report[key]}")
    return report


if __name__ == "__main__":
    main()
