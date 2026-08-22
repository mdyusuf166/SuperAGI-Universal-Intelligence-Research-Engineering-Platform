from superagi.integrations.base import OptionalIntegrationAdapter


class ROS2Adapter(OptionalIntegrationAdapter):
    def __init__(self) -> None:
        super().__init__('ros2', ('robotics_middleware',))
