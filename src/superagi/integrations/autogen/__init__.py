from superagi.integrations.base import OptionalIntegrationAdapter


class AutoGenAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('autogen', ('multi_agent_coordination',))
