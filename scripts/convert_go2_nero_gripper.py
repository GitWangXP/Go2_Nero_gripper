#!/usr/bin/env python3
# Copyright (c) 2026, Go2_Nero_Gripper project.
#
# SPDX-License-Identifier: Apache-2.0

"""Convert the merged Go2 + NERO + gripper URDF into a USD asset (LeggedManip-style).

Run once (inside the Isaac Lab Python environment) before training:

    isaaclab.bat -p scripts/convert_go2_nero_gripper.py

The generated ``go2_nero_gripper.usd`` (and its ``configuration/`` layers) are
written next to the source URDF under
``source/Go2_Nero_Gripper/Go2_Nero_Gripper/assets/go2_nero_gripper/``.
"""

import argparse
from pathlib import Path

from isaaclab.app import AppLauncher

# --------------------------------------------------------------------------
# Parse CLI args (includes the standard Isaac Sim app-launcher flags).
# --------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Convert go2_nero_gripper.urdf to USD.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

# Launch Isaac Sim first.
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

# --------------------------------------------------------------------------
# Imports after the app is running.
# --------------------------------------------------------------------------
from isaaclab.sim.converters import UrdfConverter, UrdfConverterCfg  # noqa: E402
from isaaclab.utils.dict import print_dict  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = PROJECT_ROOT / "source" / "Go2_Nero_Gripper" / "Go2_Nero_Gripper" / "assets" / "go2_nero_gripper"


def main() -> None:
    urdf_path = str((ASSET_DIR / "urdf" / "go2_nero_gripper.urdf").resolve())
    usd_dir = str(ASSET_DIR.resolve())

    cfg = UrdfConverterCfg(
        asset_path=urdf_path,
        usd_dir=usd_dir,
        usd_file_name="go2_nero_gripper.usd",
        force_usd_conversion=True,
        # Floating-base quadruped: do NOT fix the root, and keep fixed joints
        # (base_link, gripper_base) as distinct bodies so they can be referenced
        # as frames by the reward/observation/command terms.
        fix_base=False,
        merge_fixed_joints=False,
        # 关节树的根 link。None 表示交给 PhysX 自行推断
        # （即唯一没有父关节的那个 link，这里是 ``base``）。
        # URDF importer 3.0 已废弃该选项：填任何非 None 的值都只会打一条警告。
        root_link_name=None,
        # 把 URDF 的 ``<mimic>`` 关节（由主动关节带动的从动关节，常见于对称的
        # 二指夹爪）展开成互相独立、可分别驱动的普通关节。
        # 在本项目里是双重无效：本 URDF 一个 ``<mimic>`` 关节都没有
        # （gripper_joint1/2 是两个独立的移动关节，靠相反的限位实现对称），
        # 且该选项在 URDF importer 3.0 中已废弃。
        convert_mimic_joints_to_normal_joints=False,
        # Physics / geometry settings (mirror LeggedManip's go2_arx5 config.yaml).
        self_collision=False,
        collision_type="Convex Hull",
        # 缺少 ``<inertial>`` 的 link 所使用的回退密度（kg/m^3）。
        # 0.0 表示保持密度不变，即不从几何体反算质量。
        # 本 URDF 中涉及 8 个 ``*_calflower*`` 碰撞代理体和 ``front_camera``——
        # 它们在宇树官方模型里就是纯碰撞 / 纯坐标系 link，本就不带 ``<inertial>``。
        link_density=0.0,
        make_instanceable=True,
        robot_type="Mobile Manipulators",
        # No drive at the USD level: Isaac Lab injects the PD actuators at runtime
        # via ArticulationCfg.actuators (DelayedPD for legs, Implicit for arm/gripper).
        joint_drive=UrdfConverterCfg.JointDriveCfg(
            # effort 以何种方式作用到关节上：
            #   "force"        -> 按真实的力 / 力矩施加，关节响应受连杆惯量影响
            #                     （物理上更忠实）。
            #   "acceleration" -> PhysX 先把惯量归一化掉，增益与质量解耦
            #                     （调参更容易，但不物理）。
            # 面向 sim2real 保持 "force"。该属性在转换时就烧进 USD，运行时不会被
            # 改写，因此它仍然支配着驱动手臂和夹爪的 implicit actuator。
            drive_type="force",
            # "none" 会把 USD 层的刚度 / 阻尼清零，使运行时的 actuator 成为增益的
            # 唯一来源。
            target_type="none",
            gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0.0, damping=0.0),
        ),
    )

    print("URDF importer config:")
    print_dict(cfg.to_dict(), nesting=0)

    converter = UrdfConverter(cfg)
    print(f"[INFO] Generated USD file: {converter.usd_path}")


if __name__ == "__main__":
    main()
    simulation_app.close()
