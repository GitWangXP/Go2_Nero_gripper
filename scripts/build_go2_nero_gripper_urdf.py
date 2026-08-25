#!/usr/bin/env python3
# Copyright (c) 2026, Go2_Nero_Gripper project.
#
# SPDX-License-Identifier: Apache-2.0

"""Merge the Unitree Go2 URDF with the NERO arm + gripper URDF into one robot.

The script produces a single self-contained URDF
(``go2_nero_gripper.urdf``) in which the NERO arm ``base_link`` is mounted on
top of the Go2 ``base`` body via a fixed joint (``arm_base_joint``), and vendors
all referenced meshes into ``assets/go2_nero_gripper/meshes/``.

Run once from the repo root (no Isaac Sim required):

    python scripts/build_go2_nero_gripper_urdf.py
"""

from __future__ import annotations

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

# --------------------------------------------------------------------------
# Paths (reference projects are siblings of this repo)
# --------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = (
    PROJECT_ROOT
    / "source"
    / "Go2_Nero_Gripper"
    / "Go2_Nero_Gripper"
    / "assets"
    / "go2_nero_gripper"
)

GO2_URDF = PROJECT_ROOT.parent / "go2_description" / "urdf" / "go2_description.urdf"
GO2_DAE_DIR = PROJECT_ROOT.parent / "go2_description" / "dae"

NERO_DIR = (
    PROJECT_ROOT.parent
    / "isaac_so_arm101-main"
    / "src"
    / "isaac_so_arm101"
    / "robots"
    / "nero_description"
)
NERO_URDF = NERO_DIR / "urdf" / "nero_gripper.urdf"
NERO_MESH_DIR = NERO_DIR / "meshes"

# --------------------------------------------------------------------------
# Arm mount pose on the Go2 torso (tune here; verify visually in Isaac Sim).
# --------------------------------------------------------------------------
ARM_BASE_JOINT = "arm_base_joint"
ARM_BASE_PARENT = "base"
ARM_BASE_CHILD = "base_link"
ARM_BASE_XYZ = "0 0 0.057"  # top face of the 0.114 m-tall torso box
ARM_BASE_RPY = "0 0 3.14"  # preserve NERO's canonical base yaw (world_to_base_link)

# Names dropped from the NERO URDF (they are replaced by ``arm_base_joint``).
NERO_WORLD_LINK = "world"
NERO_WORLD_JOINT = "world_to_base_link"

GO2_PACKAGE_PREFIX = "package://go2_description/"
NERO_MESH_PREFIX = "../meshes/"


def _rewrite_go2_mesh(filename: str) -> str:
    if filename.startswith(GO2_PACKAGE_PREFIX):
        return "../meshes/go2/" + filename[len(GO2_PACKAGE_PREFIX):]
    return filename


def _rewrite_nero_mesh(filename: str) -> str:
    if filename.startswith(NERO_MESH_PREFIX):
        return "../meshes/nero/" + filename[len(NERO_MESH_PREFIX):]
    return filename


def _rewrite_meshes(root: ET.Element, fn) -> None:
    for mesh in root.iter("mesh"):
        if "filename" in mesh.attrib:
            mesh.set("filename", fn(mesh.attrib["filename"]))


def main() -> None:
    go2_root = ET.parse(str(GO2_URDF)).getroot()
    nero_root = ET.parse(str(NERO_URDF)).getroot()

    # Rename the combined robot.
    go2_root.set("name", "go2_nero_gripper")

    # Resolve the Go2 ``package://`` mesh references to vendored relative paths.
    _rewrite_meshes(go2_root, _rewrite_go2_mesh)

    # Strip NERO's ``world`` root and its fixed base joint.
    for link in list(nero_root.findall("link")):
        if link.get("name") == NERO_WORLD_LINK:
            nero_root.remove(link)
    for joint in list(nero_root.findall("joint")):
        if joint.get("name") == NERO_WORLD_JOINT:
            nero_root.remove(joint)

    # Resolve NERO's relative mesh references to vendored relative paths.
    _rewrite_meshes(nero_root, _rewrite_nero_mesh)

    # Build the fixed joint that mounts the arm base on the Go2 torso.
    arm_joint = ET.Element("joint", name=ARM_BASE_JOINT, type="fixed")
    ET.SubElement(arm_joint, "origin", xyz=ARM_BASE_XYZ, rpy=ARM_BASE_RPY)
    ET.SubElement(arm_joint, "parent", link=ARM_BASE_PARENT)
    ET.SubElement(arm_joint, "child", link=ARM_BASE_CHILD)

    # Append the arm joint and all remaining NERO links/joints into the Go2 tree.
    go2_root.append(arm_joint)
    for elem in list(nero_root):
        go2_root.append(elem)

    # Write the merged URDF.
    out_urdf = ASSET_DIR / "urdf" / "go2_nero_gripper.urdf"
    out_urdf.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(go2_root, space="  ")
    ET.ElementTree(go2_root).write(out_urdf, encoding="utf-8", xml_declaration=True)

    # Vendor the meshes.
    go2_dst = ASSET_DIR / "meshes" / "go2"
    nero_dst = ASSET_DIR / "meshes" / "nero"
    if go2_dst.exists():
        shutil.rmtree(go2_dst)
    shutil.copytree(GO2_DAE_DIR, go2_dst / "dae")
    if nero_dst.exists():
        shutil.rmtree(nero_dst)
    shutil.copytree(NERO_MESH_DIR, nero_dst)

    print(f"[INFO] Wrote merged URDF: {out_urdf}")
    print(f"[INFO] Vendored Go2 meshes  -> {go2_dst}")
    print(f"[INFO] Vendored NERO meshes -> {nero_dst}")


if __name__ == "__main__":
    main()
