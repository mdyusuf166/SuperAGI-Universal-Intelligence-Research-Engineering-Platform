"""Explicit ARC-09 registration artifact; callers retain registry ownership."""
from superagi.orchestration.models import AgentCapability, AgentDescriptor
def science_agent_descriptor():
    return AgentDescriptor(name="science_agent", capability=AgentCapability(domain="science", capabilities=["science", "scientific_synthesis"], task_types=["scientific_question"], safety_level="low"))
