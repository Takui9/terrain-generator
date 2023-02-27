import os
import numpy as np
import matplotlib.pyplot as plt
import trimesh
import inspect

from wfc.wfc import WFCSolver

from mesh_parts.create_tiles import create_mesh_pattern
from mesh_parts.mesh_utils import visualize_mesh
from mesh_parts.mesh_parts_cfg import MeshPartsCfg, MeshPattern

from configs.indoor_cfg import IndoorPattern, IndoorPatternLevels
from configs.navigation_cfg import IndoorNavigationPatternLevels
from alive_progress import alive_bar

from primitive_course.steps import *


def generate_tiles(
    cfg,
    mesh_name="result_mesh.stl",
    mesh_dir="results/result",
    visualize=False,
):

    dim = cfg.dim
    tiles = create_mesh_pattern(cfg)

    result_mesh = trimesh.Trimesh()
    for name, tile in tiles.items():
        if name == "start":
            mesh = tile.get_mesh().copy()
            xy_offset = np.array([0, 0.0, 0.0])
            mesh.apply_translation(xy_offset)
        elif name == "goal":
            mesh = tile.get_mesh().copy()
            xy_offset = np.array([0.0, -2 * dim[1], 0.0])
            mesh.apply_translation(xy_offset)
        else:
            mesh = tile.get_mesh().copy()
            xy_offset = np.array([0.0, -1 * dim[1], 0.0])
            mesh.apply_translation(xy_offset)
        result_mesh += mesh

    bbox = result_mesh.bounding_box.bounds
    # Get the center of the bounding box.
    center = np.mean(bbox, axis=0)
    center[2] = 0.0
    # Get the size of the bounding box.
    result_mesh = result_mesh.apply_translation(-center)

    os.makedirs(mesh_dir, exist_ok=True)
    print("saving mesh to ", mesh_name)
    result_mesh.export(os.path.join(mesh_dir, mesh_name))
    if visualize:
        visualize_mesh(result_mesh)


def generate_steps(dim, level, mesh_dir):
    height_diff = level * 1.0
    cfgs = create_step(MeshPartsCfg(dim=dim), height_diff=height_diff)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_gaps(dim, level, mesh_dir):
    gap_length = level * 0.8
    cfgs = create_gaps(MeshPartsCfg(dim=dim), gap_length=gap_length)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_gaps_with_h(dim, level, mesh_dir):
    gap_length = level * 0.8
    height_diff = level * 0.2
    cfgs = create_gaps(MeshPartsCfg(dim=dim), gap_length=gap_length, height_diff=height_diff)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_middle_steps(dim, level, mesh_dir):
    height_diff = level * 0.5
    n = 11
    cfgs = create_middle_step(MeshPartsCfg(dim=dim), height_diff=height_diff)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_middle_steps_wide(dim, level, mesh_dir):
    height_diff = level * 0.5
    n = 5
    cfgs = create_middle_step(MeshPartsCfg(dim=dim), height_diff=height_diff, n=n)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_narrows(dim, level, mesh_dir):
    width = (1.0 - level) * 0.5 + 0.5
    side_std = 0.0
    height_std = 0.0
    cfgs = create_narrow(MeshPartsCfg(dim=dim), width=width, side_std=side_std, height_std=height_std)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_narrows_with_side(dim, level, mesh_dir):
    width = (1.0 - level) * 0.5 + 0.5
    side_std = 0.1 * level
    height_std = 0.0
    cfgs = create_narrow(MeshPartsCfg(dim=dim), width=width, side_std=side_std, height_std=height_std)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_narrows_with_side_height(dim, level, mesh_dir):
    width = (1.0 - level) * 0.5 + 0.5
    side_std = 0.1 * level
    height_std = 0.05 * level
    cfgs = create_narrow(MeshPartsCfg(dim=dim), width=width, side_std=side_std, height_std=height_std)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_box_grid(dim, level, mesh_dir):
    height_diff = 0.0
    height_std = level * 0.5
    n = 8
    cfgs = create_box_grid(MeshPartsCfg(dim=dim), height_diff=height_diff, height_std=height_std, n=n)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_box_grid_slope(dim, level, mesh_dir):
    height_diff = level * 1.5
    height_std = level * 0.5
    n = 8
    cfgs = create_box_grid(MeshPartsCfg(dim=dim), height_diff=height_diff, height_std=height_std, n=n)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_box_grid_small(dim, level, mesh_dir):
    height_diff = level * 1.5
    height_std = level * 0.5
    n = 14
    cfgs = create_box_grid(MeshPartsCfg(dim=dim), height_diff=height_diff, height_std=height_std, n=n)
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_floating_box_grid(dim, level, mesh_dir):
    height_diff = 0.0
    height_gap = (1.0 - level) * 1.0 + 0.5
    height_std = 0.2 * level
    cfgs = create_floating_box_grid(
        MeshPartsCfg(dim=dim),
        height_diff=height_diff,
        height_std=height_std,
        height_gap_mean=height_gap,
        height_gap_std=0.1,
        n=4,
    )
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_floating_box_grid_slope(dim, level, mesh_dir):
    height_diff = level * 1.5
    height_gap = (1.0 - level) * 1.0 + 0.5
    cfgs = create_floating_box_grid(
        MeshPartsCfg(dim=dim),
        height_diff=height_diff,
        height_std=0.1,
        height_gap_mean=height_gap,
        height_gap_std=0.1,
        n=4,
    )
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_random_tunnel(dim, level, mesh_dir):
    height_diff = 0.0
    height_gap = (1.0 - level) * 1.0 + 0.5
    cfgs = create_random_tunnel(
        MeshPartsCfg(dim=dim),
        height_diff=height_diff,
        height_std=0.1,
        height_gap_mean=height_gap,
        height_gap_std=0.1,
        n=8,
        wall_n=2,
    )
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_random_tunnel_narrow(dim, level, mesh_dir):
    height_diff = 0.0
    height_gap = (1.0 - level) * 1.0 + 0.5
    cfgs = create_random_tunnel(
        MeshPartsCfg(dim=dim),
        height_diff=height_diff,
        height_std=0.1,
        height_gap_mean=height_gap,
        height_gap_std=0.1,
        n=6,
        wall_n=2,
    )
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


def generate_random_tunnel_slope(dim, level, mesh_dir):
    height_diff = 1.5 * level
    height_gap = (1.0 - level) * 1.0 + 0.5
    cfgs = create_random_tunnel(
        MeshPartsCfg(dim=dim),
        height_diff=height_diff,
        height_std=0.1,
        height_gap_mean=height_gap,
        height_gap_std=0.1,
        n=8,
        wall_n=2,
    )
    cfg = MeshPattern(dim=dim, mesh_parts=cfgs)
    mesh_dir = os.path.join(mesh_dir, inspect.currentframe().f_code.co_name)
    generate_tiles(cfg, mesh_name=f"mesh_{level:.1f}.obj", mesh_dir=mesh_dir)


if __name__ == "__main__":

    dim = (3.0, 3.0, 3.0)
    level = 0.5
    mesh_dir = "results/primitive"

    for level in np.arange(0.0, 1.1, 0.1):
        generate_steps(dim, level, mesh_dir)
        generate_gaps(dim, level, mesh_dir)
        generate_gaps_with_h(dim, level, mesh_dir)
        generate_middle_steps(dim, level, mesh_dir)
        generate_middle_steps_wide(dim, level, mesh_dir)
        generate_narrows(dim, level, mesh_dir)
        generate_narrows_with_side(dim, level, mesh_dir)
        generate_narrows_with_side_height(dim, level, mesh_dir)
        generate_box_grid(dim, level, mesh_dir)
        generate_box_grid_slope(dim, level, mesh_dir)
        generate_box_grid_small(dim, level, mesh_dir)
        generate_floating_box_grid(dim, level, mesh_dir)
        generate_floating_box_grid_slope(dim, level, mesh_dir)
        generate_random_tunnel(dim, level, mesh_dir)
        generate_random_tunnel_narrow(dim, level, mesh_dir)
        generate_random_tunnel_slope(dim, level, mesh_dir)