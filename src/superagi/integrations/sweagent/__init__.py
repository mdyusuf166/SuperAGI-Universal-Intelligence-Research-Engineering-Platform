from superagi.integrations.base import OptionalIntegrationAdapter


class SWEAgentAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('sweagent', ('issue_resolution',))
