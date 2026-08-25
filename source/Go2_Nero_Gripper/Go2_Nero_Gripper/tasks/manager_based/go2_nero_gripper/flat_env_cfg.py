# Copyright (c) 2026, Go2_Nero_Gripper project.
#
# SPDX-License-Identifier: Apache-2.0

"""Flat-terrain whole-body (locomotion + end-effector pose tracking) task config."""

from isaaclab.assets import ArticulationCfg
from isaaclab.utils import configclass

from Go2_Nero_Gripper.assets.go2_nero_gripper.go2_nero_gripper_articulation_cfg import GO2_NERO_GRIPPER_CFG

from .go2_nero_gripper_env_cfg import Go2NeroGripperEnvCfg


@configclass
class Go2NeroGripperFlatEnvCfg(Go2NeroGripperEnvCfg):
    def __post_init__(self) -> None:
        # post init of parent
        super().__post_init__()

        # scene
        self.scene.robot: ArticulationCfg = GO2_NERO_GRIPPER_CFG.replace(
            prim_path="{ENV_REGEX_NS}/Robot"
        )

        # commands (NERO arm workspace, in ``base_link`` frame; tune after visual check)
        self.commands.ee_pose.limit_ranges.pos_x = (0.25, 0.55)
        self.commands.ee_pose.limit_ranges.pos_y = (-0.35, 0.35)
        self.commands.ee_pose.limit_ranges.pos_z = (0.1, 0.5)

        # events
        self.events.push_robot = None

        # actions
        self.actions.joint_pos.scale = 0.25
        self.actions.joint_pos.clip = {".*": (-10.0, 10.0)}

        # rewards
        self.rewards.track_base_height_exp.params["target_height"] = 0.3

        self.disable_zero_weight_rewards()


class Go2NeroGripperFlatEnvCfg_PLAY(Go2NeroGripperFlatEnvCfg):
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
