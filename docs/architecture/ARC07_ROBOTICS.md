# ARC-07 Robotics

ARC-07 is a simulation-first robotics research foundation. It includes typed robots/states/sensor readings, deterministic grid A* planning, trajectory construction, and PID simulation control. Physical commands are denied by default by `RoboticsSafetyPolicy`; there is no hardware fallback or command execution. ROS 2, Navigation2, Gazebo, Isaac Lab, and Gymnasium remain optional future adapter boundaries.
