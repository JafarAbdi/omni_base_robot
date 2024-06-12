# Copyright (c) 2023 PAL Robotics S.L. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from pathlib import Path

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration

from launch_pal.arg_utils import read_launch_argument
from launch_pal.robot_utils import (get_laser_model,
                                    get_robot_name)
from launch_param_builder import load_xacro
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def declare_args(context, *args, **kwargs):

    sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='False',
        description='Use simulation time')

    public_sim_arg = DeclareLaunchArgument(
        'is_public_sim', default_value='False',
        description='Use public simulation')

    rgbd_sensors_arg = DeclareLaunchArgument(
        'rgbd_sensors', default_value='False',
        description='Use rgbd sensors'
    )
    robot_name = read_launch_argument('robot_name', context)

    return [get_laser_model(robot_name),
            sim_time_arg,
            public_sim_arg,
            rgbd_sensors_arg]


def launch_setup(context, *args, **kwargs):

    robot_description_content = load_xacro(
        Path(os.path.join(
            get_package_share_directory('omni_base_description'), 'robots',
            'omni_base.urdf.xacro')),
        {
            'laser_model': read_launch_argument('laser_model', context),
            'use_sim': read_launch_argument('use_sim_time', context),
            'public_sim': read_launch_argument('is_public_sim', context),
            'rgbd_sensors': read_launch_argument('rgbd_sensors', context),
        },
    )

    robot_description = ParameterValue(robot_description_content, value_type=None)
    # which parses the param as YAML instead of string
    rsp = Node(package='robot_state_publisher',
               executable='robot_state_publisher',
               output='both',
               parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time'),
                            "robot_description": robot_description}])

    return [rsp]


def generate_launch_description():

    ld = LaunchDescription()

    # Declare arguments
    # we use OpaqueFunction so the callbacks have access to the context
    ld.add_action(get_robot_name('omni_base'))
    ld.add_action(OpaqueFunction(function=declare_args))

    # Execute robot_state_publisher node
    ld.add_action(OpaqueFunction(function=launch_setup))

    return ld
