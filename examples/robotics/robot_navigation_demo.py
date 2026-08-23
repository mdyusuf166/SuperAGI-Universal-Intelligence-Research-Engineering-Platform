from superagi.robotics import Robot,AStarPlanner,MotionPlanner,PIDController
from superagi.robotics.models import RobotCommand
from superagi.robotics.safety import RoboticsSafetyPolicy
r=Robot(name="mock-mobile");path=AStarPlanner().plan((0,0),(3,0),{(1,1)});trajectory=MotionPlanner().plan(path);control=PIDController().compute(1,0);safety=RoboticsSafetyPolicy().assess(RobotCommand(command_type="move"))
print("SUPERAGI ARC-07 ROBOTICS DEMO\nRobot:",r.name,"\nPath:",path,"\nTrajectory:",trajectory,"\nControl:",control,"\nSafety:",safety,"\nSIMULATION ONLY — NO PHYSICAL ROBOT CONTROL")
