from ..models import Trajectory
class MotionPlanner:
 def plan(self,path,velocity=1,acceleration=1):
  if velocity<=0 or acceleration<=0:raise ValueError("limits must be positive")
  return Trajectory(waypoints=path,timestamps=[i/velocity for i in range(len(path))],velocity_limits=velocity,acceleration_limits=acceleration)
