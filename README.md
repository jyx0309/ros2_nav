# ros2_nav

ROS 2 Jazzy + Gazebo Sim navigation learning project.

## Robot Variants

The project includes two Gazebo robot variants for comparison:

- Two-wheel differential drive with a passive caster:

  ```bash
  ros2 launch my_robot_gazebo gazebo.launch.py
  ```

- Four-wheel skid-steer differential drive:

  ```bash
  ros2 launch my_robot_gazebo gazebo_four_wheel.launch.py
  ```

Both variants publish the same ROS-facing topics and frames:

- `/cmd_vel`
- `/odom`
- `/scan`
- `odom -> base_footprint`
- `base_footprint -> base_link -> laser_link`

Use the two-wheel caster model as the stable Nav2 / SLAM baseline. Use the
four-wheel skid-steer model to study how lateral wheel slip and Gazebo contact
friction affect odometry and SLAM.
