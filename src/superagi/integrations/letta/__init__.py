from superagi.integrations.base import OptionalIntegrationAdapter


class LettaAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('letta', ('persistent_memory', 'stateful_agents'))
