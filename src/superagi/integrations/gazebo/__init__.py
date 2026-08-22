from superagi.integrations.base import OptionalIntegrationAdapter


class GazeboAdapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('gazebo', ('robot_simulation',))
