import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    # 패키지 share 경로
    pkg_share = get_package_share_directory('my_robot_description')


    # 1) Xacro 파일 경로
    xacro_file = os.path.join(pkg_share, 'urdf', 'amr_robot.urdf.xacro')

    # 2) xacro -> robot_description 변환
    robot_description = ParameterValue(
        Command
        (['xacro ', xacro_file]),
        value_type=str
    )

    # 3) Gazebo 기본 Launch 포함 (--verbose)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            )
        ]),
        launch_arguments={'verbose': 'true'}.items()
    )

    # 4) robot_state_publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'robot_description': robot_description
        }]
    )

    # 5) Gazebo에 로봇 스폰
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'amr_robot'
        ],
        output='screen'
    )

    # 6) joint_state_broadcaster 스포너
    joint_state_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '-c', '/controller_manager'],
        output='screen'
    )

    # 7) diff_drive_controller 스포너
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '-c', '/controller_manager'],
        output='screen'
    )

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        joint_state_spawner,
        diff_drive_spawner
    ])
