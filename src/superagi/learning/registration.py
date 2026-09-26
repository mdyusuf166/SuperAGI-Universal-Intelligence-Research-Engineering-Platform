"""Register learning agents on the existing ARC-01 and ARC-09 registries."""

from superagi.orchestration.models import AgentCapability, AgentDescriptor

from .agents import AGENT_CLASSES


def learning_descriptors(agents=None):
    selected = agents if agents is not None else [cls() for cls in AGENT_CLASSES]
    return [
        AgentDescriptor(
            name=agent.metadata.name,
            capability=AgentCapability(domain="learning", capabilities=list(agent.metadata.capabilities), task_types=["learning"], safety_level=agent.metadata.risk_level, available=True),
        )
        for agent in selected
    ]


def register_learning_agents(agent_registry, capability_registry=None):
    created = [cls() for cls in AGENT_CLASSES]
    for agent in created:
        agent_registry.register(agent)
    if capability_registry is not None:
        for descriptor in learning_descriptors(created):
            capability_registry.register(descriptor)
    return created
