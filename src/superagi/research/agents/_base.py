from superagi.core.agents import BaseAgent
from superagi.core.models import AgentMetadata


def metadata(name: str, description: str, capabilities: tuple[str, ...], required_tools: tuple[str, ...] = ()) -> AgentMetadata:
    return AgentMetadata(name=name, description=description, capabilities=capabilities, required_tools=required_tools, risk_level="low")


class ResearchAgent(BaseAgent):
    pass
