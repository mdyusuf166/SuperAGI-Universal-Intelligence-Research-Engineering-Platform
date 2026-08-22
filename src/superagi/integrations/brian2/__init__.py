from superagi.integrations.base import OptionalIntegrationAdapter


class Brian2Adapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('brian2', ('spiking_neural_networks',))
