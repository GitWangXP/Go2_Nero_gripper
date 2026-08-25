# Copyright (c) 2026, Go2_Nero_Gripper project.
#
# SPDX-License-Identifier: Apache-2.0

"""Whole-body control (WBC, mixed-frame EE pose) task config."""

from isaaclab.assets import ArticulationCfg
from isaaclab.utils import configclass

from Go2_Nero_Gripper.assets.go2_nero_gripper.go2_nero_gripper_articulation_cfg import GO2_NERO_GRIPPER_CFG

from . import mdp
from .go2_nero_gripper_env_cfg import Go2NeroGripperEnvCfg


@configclass
class WBCCommandsCfg:
    """Command specifications for the MDP (mixed-frame EE pose)."""

    ee_pose = mdp.command_cfg.UniformPoseWBCCommandCfg(
        asset_name="robot",
        body_name="gripper_base",
        resampling_time_range=(8.0, 10.0),
        debug_vis=True,
        ranges=mdp.command_cfg.UniformPoseWBCCommandCfg.Ranges(
            pos_x=(0.4, 0.45),
            pos_y=(-0.05, 0.05),
            pos_z=(0.5, 0.5),  # world frame
            roll=(-0.0, 0.0),
            pitch=(-0.0, -0.0),  # depends on end-effector axis
            yaw=(-0.0, -0.0),
        ),
        limit_ranges=mdp.command_cfg.UniformPoseWBCCommandCfg.Ranges(
            pos_x=(0.55, 0.7),
            pos_y=(-0.35, 0.35),
            pos_z=(0.1, 0.8),  # world frame
            roll=(-3.14 / 3, 3.14 / 3),
            pitch=(-3.14 / 4, 3.14 / 4),
            yaw=(-3.14 / 6, 3.14 / 6),
        ),
    )

    base_velocity = mdp.command_cfg.UniformVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(10.0, 10.0),
        rel_standing_envs=0.1,
        debug_vis=True,
        heading_command=False,
        ranges=mdp.command_cfg.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-0.2, 0.2),
            lin_vel_y=(-0.2, 0.2),
            ang_vel_z=(-0.2, 0.2),
            heading=(-0.0, 0.0),
        ),
        limit_ranges=mdp.command_cfg.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-1.0, 1.0),
            lin_vel_y=(-0.6, 0.6),
            ang_vel_z=(-1.0, 1.0),
            heading=(-0.0, 0.0),
        ),
    )


@configclass
class Go2NeroGripperWBCEnvCfg(Go2NeroGripperEnvCfg):
    commands: WBCCommandsCfg = WBCCommandsCfg()

    def __post_init__(self) -> None:
        # post init of parent
        super().__post_init__()

        # scene
        self.scene.robot: ArticulationCfg = GO2_NERO_GRIPPER_CFG.replace(
            prim_path="{ENV_REGEX_NS}/Robot"
        )

        # events
        self.events.push_robot = None

        # actions
        self.actions.joint_pos.scale = 0.25
        self.actions.joint_pos.clip = {".*": (-10.0, 10.0)}

        # rewards (WBC re-weighting, mirrors LeggedManip go2_arx5 WBC)
        self.rewards.track_base_height_exp.params["target_height"] = 0.28
        self.rewards.end_effector_position_tracking_exp.func = mdp.position_command_error_exp
        self.rewards.end_effector_position_tracking_exp.weight = 4.5
        self.rewards.end_effector_orientation_tracking.weight = -4.0
        self.rewards.track_lin_vel_xy_exp.weight = 3.5
        self.rewards.track_ang_vel_z_exp.weight = 2.5
        self.rewards.track_base_height_exp.weight = 0.25
        self.rewards.flat_orientation_l2.weight = -0.5
        self.rewards.feet_long_air.weight = -1.0
        self.rewards.air_time_variance.weight = -1.5

        self.disable_zero_weight_rewards()


class Go2NeroGripperWBCEnvCfg_PLAY(Go2NeroGripperWBCEnvCfg):
    def __post_init__(self) -> None:
        # post init of parent
        super().__post_init__()
        # make a smaller scene for play
        self.scene.num_envs = 50
        self.scene.env_spacing = 2.5
        # disable randomization for play
        self.observations.policy.enable_corruption = False
        # use the full command ranges
        self.commands.base_velocity.ranges = self.commands.base_velocity.limit_ranges
        self.commands.ee_pose.ranges = self.commands.ee_pose.limit_ranges
