import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_description')

    # 로봇 Xacro 파일 경로
    xacro_file = os.path.join(pkg_share, 'urdf', 'amr_robot.urdf.xacro')

    # xacro -> robot_description 파라미터 변환
    robot_description = ParameterValue(Command([
        'xacro ',
        xacro_file
    ]), value_type=str)


    # Gazebo 기본 Launch 포함 (verbose 모드)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py'
        )]),
        launch_arguments={'verbose': 'true'}.items()
    )

    # robot_state_publisher (TF, URDF 퍼블리시)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[
            {'use_sim_time': True,
             'robot_description': robot_description}
        ]
    )

    # Gazebo 상에 로봇 스폰
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'amr_robot'
        ],
        output='screen'
    )

    # Diff Drive Controller Spawner
    # ros2 run controller_manager spawner diff_drive_controller -c /controller_manager
    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner.py',
        arguments=['diff_drive_controller', '-c', '/controller_manager'],
        output='screen'
    )
    
    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_entity,
        diff_drive_spawner
    ])