# Copyright (c) 2026, Go2_Nero_Gripper project.
#
# SPDX-License-Identifier: Apache-2.0

"""Gym environment registration for the Go2 + NERO + gripper tasks."""

import gymnasium as gym

from . import agents

##
# Register Gym environments.
##

# Flat
gym.register(
    id="GO2-NERO-Gripper-Flat",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.flat_env_cfg:Go2NeroGripperFlatEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2NeroGripperFlatPPORunnerCfg",
    },
)

gym.register(
    id="GO2-NERO-Gripper-Flat-Play",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.flat_env_cfg:Go2NeroGripperFlatEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2NeroGripperFlatPPORunnerCfg",
    },
)

# WBC
gym.register(
    id="GO2-NERO-Gripper-WBC",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.wbc_env_cfg:Go2NeroGripperWBCEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2NeroGripperWBCPPORunnerCfg",
    },
)

gym.register(
    id="GO2-NERO-Gripper-WBC-Play",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.wbc_env_cfg:Go2NeroGripperWBCEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:Go2NeroGripperWBCPPORunnerCfg",
    },
)
