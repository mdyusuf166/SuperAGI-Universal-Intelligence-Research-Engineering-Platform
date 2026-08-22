from superagi.integrations.base import OptionalIntegrationAdapter


class NestAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('nest', ('neural_simulation',))
