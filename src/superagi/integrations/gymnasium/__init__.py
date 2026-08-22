from superagi.integrations.base import OptionalIntegrationAdapter


class GymnasiumAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('gymnasium', ('reinforcement_learning', 'simulation'))
