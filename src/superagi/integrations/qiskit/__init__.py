from superagi.integrations.base import OptionalIntegrationAdapter


class QiskitAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('qiskit', ('quantum_circuits',))
