import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    slam_pkg_share = get_package_share_directory('my_robot_slam')

    slam_params_file = os.path.join(
        slam_pkg_share,
        'config',
        'slam_toolbox.yaml'
    )

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params_file],
        respawn=True,
        respawn_delay=2.0
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_slam',
        output='screen',
        parameters=[
            {
                'use_sim_time': True,
                'autostart': True,
                'node_names': ['slam_toolbox']
            }
        ]
    )
    return LaunchDescription([
        slam_toolbox_node,
        rviz_node,
        lifecycle_manager
    ])
