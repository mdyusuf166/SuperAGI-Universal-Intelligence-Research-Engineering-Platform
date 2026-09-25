"""Register world-model agents on the existing ARC-01 and ARC-09 registries."""

from superagi.orchestration.models import AgentCapability, AgentDescriptor

from .agents import ConflictDetectionAgent, KnowledgeGraphAgent, WorldModelAgent, WorldQueryAgent, WorldStateAgent

AGENT_CLASSES = (
    WorldModelAgent,
    KnowledgeGraphAgent,
    WorldQueryAgent,
    ConflictDetectionAgent,
    WorldStateAgent,
)


def world_model_descriptors(agents=None):
    selected = agents if agents is not None else [cls() for cls in AGENT_CLASSES]
    return [
        AgentDescriptor(
            name=agent.metadata.name,
            capability=AgentCapability(domain="world_model", capabilities=list(agent.metadata.capabilities), task_types=["world_model"], safety_level=agent.metadata.risk_level, available=True),
        )
        for agent in selected
    ]


def register_world_model_agents(agent_registry, capability_registry=None):
    created = [cls() for cls in AGENT_CLASSES]
    for agent in created:
        agent_registry.register(agent)
    if capability_registry is not None:
        for descriptor in world_model_descriptors(created):
            capability_registry.register(descriptor)
    return created
