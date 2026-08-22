from superagi.integrations.base import OptionalIntegrationAdapter


class IsaacAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('isaac', ('robot_learning',))
