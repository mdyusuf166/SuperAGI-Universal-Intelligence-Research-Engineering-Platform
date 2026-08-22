from superagi.integrations.base import OptionalIntegrationAdapter


class DeepChemAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('deepchem', ('molecular_modeling',))
