from superagi.integrations.base import OptionalIntegrationAdapter


class PennyLaneAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('pennylane', ('hybrid_quantum_classical',))
