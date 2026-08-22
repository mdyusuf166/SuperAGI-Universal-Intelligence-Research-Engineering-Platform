from superagi.integrations.base import OptionalIntegrationAdapter


class BiomniAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('biomni', ('biomedical_research', 'bioinformatics'))
