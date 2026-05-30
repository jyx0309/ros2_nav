import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command

from launch_ros.actions import Node


def generate_launch_description():
    # =====================
    # Package paths
    # =====================

    gazebo_pkg_share = get_package_share_directory('my_robot_gazebo')
    description_pkg_share = get_package_share_directory('my_robot_description')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    world_path = os.path.join(
        gazebo_pkg_share,
        'worlds',
        'obstacle.sdf'
    )

    xacro_path = os.path.join(
        description_pkg_share,
        'urdf',
        'my_robot.urdf.xacro'
    )

    # =====================
    # Robot description
    # =====================

    robot_description_content = Command([
        'xacro ',
        xacro_path
    ])

    robot_description_param = {
        'robot_description': robot_description_content,
        'use_sim_time': True
    }

    # =====================
    # Gazebo Sim
    # =====================

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                ros_gz_sim_share,
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': f'-r {world_path}'
        }.items()
    )

    # =====================
    # Robot state publisher
    # =====================

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description_param]
    )

    joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )
    # =====================
    # Spawn robot into Gazebo
    # =====================

    spawn_robot = TimerAction(
        period=3.0,
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-name', 'my_robot',
                    '-topic', 'robot_description',
                    '-x', '0',
                    '-y', '0',
                    '-z', '0.02'
                ],
                output='screen'
            )
        ]
    )

    # =====================
    # Bridges
    # =====================

    cmd_vel_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='cmd_vel_bridge',
        arguments=[
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
        ],
        output='screen'
    )

    odom_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='odom_bridge',
        arguments=[
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry'
        ],
        output='screen'
    )

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ],
        output='screen'
    )

    scan_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='scan_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        output='screen'
    )

    tf_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='tf_bridge',
        arguments=[
             '/model/my_robot/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
        ],
        remappings=[
             ('/model/my_robot/tf', '/tf')
        ],
        output='screen'
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        joint_state_publisher,
        spawn_robot,
        cmd_vel_bridge,
        odom_bridge,
        clock_bridge,
        scan_bridge,
        tf_bridge
    ])