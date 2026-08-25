# Copyright (c) 2026, Go2_Nero_Gripper project.
#
# SPDX-License-Identifier: Apache-2.0

"""Configuration for the Go2 + NERO-arm + gripper robot.

Combines:
  * Unitree Go2 legs (12 joints: ``{FL,FR,RL,RR}_{hip,thigh,calf}_joint``),
    actuated with ``DelayedPDActuatorCfg`` (LeggedManip_Lab Go2 gains).
  * NERO 7-DOF arm (``joint1..joint7``) + 2-jaw gripper (``gripper_joint1/2``),
    actuated with ``ImplicitActuatorCfg`` (official ``isaac_so_arm101`` NERO config).
"""

import os

import isaaclab.sim as sim_utils
from isaaclab.actuators import DelayedPDActuatorCfg, ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

current_dir = os.path.dirname(os.path.abspath(__file__))

GO2_NERO_GRIPPER_USD = os.path.join(current_dir, "go2_nero_gripper.usd")

##
# Configuration
##


GO2_NERO_GRIPPER_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=GO2_NERO_GRIPPER_USD,
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
        ),
        # collision_props=sim_utils.CollisionPropertiesCfg(
        #     collision_enabled=True,
        #     contact_offset=0.02,
        #     rest_offset=0.005 ,
        # ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.4),
        joint_pos={
            # legs
            "FL_hip_joint": 0.1,
            "FR_hip_joint": -0.1,
            "RL_hip_joint": 0.1,
            "RR_hip_joint": -0.1,
            "FL_thigh_joint": 0.8,
            "FR_thigh_joint": 0.8,
            "RL_thigh_joint": 1.0,
            "RR_thigh_joint": 1.0,
            "FL_calf_joint": -1.5,
            "FR_calf_joint": -1.5,
            "RL_calf_joint": -1.5,
            "RR_calf_joint": -1.5,
            # arm (NERO home pose)
            "joint1": 0.0,
            "joint2": 0.0,
            "joint3": 0.0,
            "joint4": 2.0,
            "joint5": 0.0,
            "joint6": 0.0,
            "joint7": 0.0,
            # gripper (open)
            "gripper_joint1": 0.05,
            "gripper_joint2": -0.05,
        },
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.9,
    actuators={
        "base_legs": DelayedPDActuatorCfg(
            joint_names_expr=[".*_hip_joint", ".*_thigh_joint", ".*_calf_joint"],
            stiffness=30.0,
            damping=0.6,
            armature=0.01,
            min_delay=0,
            max_delay=4,
            friction=0.01,
        ),
        "arm": ImplicitActuatorCfg(
            joint_names_expr=["joint.*"],
            effort_limit=25.0,
            velocity_limit=1.5,
            stiffness={
                "joint1": 200.0,
                "joint2": 170.0,
                "joint3": 120.0,
                "joint4": 80.0,
                "joint5": 50.0,
                "joint6": 20.0,
                "joint7": 10.0,
            },
            damping={
                "joint1": 100.0,
                "joint2": 60.0,
                "joint3": 70.0,
                "joint4": 24.0,
                "joint5": 20.0,
                "joint6": 10.0,
                "joint7": 5.0,
            },
        ),
        "gripper": ImplicitActuatorCfg(
            joint_names_expr=["gripper_joint1", "gripper_joint2"],
            effort_limit_sim=22.0,
            velocity_limit_sim=1.5,
            stiffness=800.0,
            damping=20.0,
        ),
    },
)
