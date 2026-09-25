"""Register collaboration agents with the existing ARC-01 and ARC-09 registries."""

from superagi.orchestration.models import AgentCapability, AgentDescriptor

from .agents import (
    CollaborationAgent,
    CommunicationAgent,
    CoordinationAgent,
    DecisionSupportAgent,
    PlanningAgent,
    ReviewAgent,
)

AGENT_CLASSES = (
    CollaborationAgent,
    PlanningAgent,
    CoordinationAgent,
    DecisionSupportAgent,
    CommunicationAgent,
    ReviewAgent,
)

_DOMAINS = {
    "collaboration_agent": "collaboration",
    "planning_agent": "planning",
    "coordination_agent": "coordination",
    "decision_support_agent": "decision_support",
    "communication_agent": "collaboration",
    "review_agent": "collaboration",
}


def collaboration_descriptors(agents=None):
    selected = agents if agents is not None else [cls() for cls in AGENT_CLASSES]
    return [
        AgentDescriptor(
            name=agent.metadata.name,
            capability=AgentCapability(
                domain=_DOMAINS[agent.metadata.name],
                capabilities=list(agent.metadata.capabilities),
                task_types=["collaboration"],
                safety_level=agent.metadata.risk_level,
                available=True,
            ),
        )
        for agent in selected
    ]


def register_collaboration_agents(agent_registry, capability_registry=None):
    created = []
    for cls in AGENT_CLASSES:
        agent = cls()
        agent_registry.register(agent)
        created.append(agent)
    if capability_registry is not None:
        for descriptor in collaboration_descriptors(created):
            capability_registry.register(descriptor)
    return created
