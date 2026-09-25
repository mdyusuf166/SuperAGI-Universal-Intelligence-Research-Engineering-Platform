"""Register engineering agents with the existing ARC-01 and ARC-09 registries."""

from superagi.orchestration.models import AgentCapability, AgentDescriptor

from .agents import (
    ArchitectureAgent,
    CircuitDesignAgent,
    ControlAgent,
    DesignReviewAgent,
    EmbeddedAgent,
    EngineeringAgent,
    SystemsEngineeringAgent,
)

AGENT_CLASSES = (
    EngineeringAgent,
    SystemsEngineeringAgent,
    CircuitDesignAgent,
    EmbeddedAgent,
    ControlAgent,
    ArchitectureAgent,
    DesignReviewAgent,
)


def engineering_descriptors(agents=None):
    selected = agents if agents is not None else [cls() for cls in AGENT_CLASSES]
    return [
        AgentDescriptor(
            name=agent.metadata.name,
            capability=AgentCapability(
                domain="engineering",
                capabilities=list(agent.metadata.capabilities),
                task_types=["engineering_design"],
                safety_level=agent.metadata.risk_level,
                available=True,
            ),
        )
        for agent in selected
    ]


def register_engineering_agents(agent_registry, capability_registry=None):
    created = []
    for cls in AGENT_CLASSES:
        agent = cls()
        agent_registry.register(agent)
        created.append(agent)
    if capability_registry is not None:
        for descriptor in engineering_descriptors(created):
            capability_registry.register(descriptor)
    return created
