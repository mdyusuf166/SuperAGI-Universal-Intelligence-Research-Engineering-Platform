from superagi.integrations.base import OptionalIntegrationAdapter


class ChempropAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('chemprop', ('molecular_property_prediction',))
