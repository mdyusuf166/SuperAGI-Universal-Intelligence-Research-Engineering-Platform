from superagi.integrations.base import OptionalIntegrationAdapter


class RDKitAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('rdkit', ('cheminformatics', 'molecular_graphs'))
