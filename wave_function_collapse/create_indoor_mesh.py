import numpy as np
from typing import Tuple
import functools

from wfc.tiles import Tile, ArrayTile, MeshTile, MeshGeneratorTile
from mesh_parts.indoor_parts import create_wall_mesh
from mesh_parts.mesh_parts_cfg import MeshPartsCfg, WallMeshPartsCfg, MeshPattern
from mesh_parts.mesh_utils import get_height_array_of_mesh


def create_wall_meshtile(cfg: WallMeshPartsCfg):
    # array = np.zeros((3, 3))
    name = cfg.name
    for edge in cfg.wall_edges:
        name += f"_{edge}"
    if cfg.use_generator:
        mesh_gen = functools.partial(create_wall_mesh, cfg)
        mesh = mesh_gen()
        array = get_height_array_of_mesh(mesh, cfg.dim, 5)
        return MeshGeneratorTile(name, array, mesh_gen, weight=cfg.weight)
    else:
        mesh = create_wall_mesh(cfg)
        array = get_height_array_of_mesh(mesh, cfg.dim, 5)
        return MeshTile(name, array, mesh, weight=cfg.weight)


def create_mesh_pattern(cfg: MeshPattern):
    tiles = []
    for k, v in cfg.__dict__.items():
        if isinstance(v, MeshPartsCfg):
            tiles += create_wall_meshtile(v).get_all_tiles(rotations=v.rotations, flips=v.flips)
    tile_dict = {tile.name: tile for tile in tiles}
    return tile_dict

# def create_wall_tiles(dim: Tuple[float, float, float] = (2.0, 2.0, 2.0)):
#     tiles = []
#     cfg = WallMeshPartsCfg(dim=dim, wall_edges=())
#     tiles += create_wall_meshtile(cfg).get_all_tiles()
# 
#     # cfg = WallMeshPartsCfg(dim=dim, wall_edges=("left",))
#     # tiles += create_wall_meshtile(cfg).get_all_tiles(rotations=(90, 180, 270), flips=())
#     # 
#     # cfg = WallMeshPartsCfg(dim=dim, wall_edges=("left", "up"))
#     # tiles += create_wall_meshtile(cfg).get_all_tiles(rotations=(90, 180, 270), flips=())
# 
#     cfg = WallMeshPartsCfg(dim=dim, wall_edges=("middle_left", "middle_right"))
#     tiles += create_wall_meshtile(cfg).get_all_tiles(rotations=(90, 180, 270), flips=())
# 
#     # cfg = WallMeshPartsCfg(dim=dim, wall_edges=("left", "up"))
#     cfg = WallMeshPartsCfg(dim=dim, wall_edges=("middle_left", "middle_bottom"))
#     tiles += create_wall_meshtile(cfg).get_all_tiles(rotations=(90, 180, 270), flips=())
# 
#     tile_dict = {tile.name: tile for tile in tiles}
# 
#     # cfg = WallMeshPartsCfg(wall_edges=("left", "up", "right"))
#     # tiles += create_wall_meshtile(cfg).get_all_tiles(rotations=(90, 180, 270), flips=())
# 
#     return tile_dict
