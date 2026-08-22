from superagi.integrations.base import OptionalIntegrationAdapter


class MCPAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('mcp', ('tool_interoperability', 'resource_interoperability'))
