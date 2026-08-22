from superagi.integrations.base import OptionalIntegrationAdapter


class OpenHandsAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('openhands', ('software_engineering_agents',))
