from superagi.integrations.base import OptionalIntegrationAdapter


class CORALAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('coral', ('continuous_evaluation', 'controlled_self_improvement'))
