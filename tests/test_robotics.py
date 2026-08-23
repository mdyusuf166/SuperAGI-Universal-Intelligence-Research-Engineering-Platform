from superagi.robotics import Robot, AStarPlanner, MotionPlanner, PIDController
from superagi.robotics.safety import RoboticsSafetyPolicy
from superagi.robotics.models import RobotCommand
def test_navigation_and_safety():
 path=AStarPlanner().plan((0,0),(2,0),{(1,1)}); assert len(path)==3; assert MotionPlanner().plan(path).waypoints==path; assert PIDController().compute(1,0)["classification"]=="SIMULATION CONTROL"
 assert not RoboticsSafetyPolicy().assess(RobotCommand(command_type="move")).allowed
