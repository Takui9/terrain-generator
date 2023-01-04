import numpy as np
import matplotlib.pyplot as plt
import trimesh

from wfc.wfc import WFCSolver

# from wfc.tiles import Tile, ArrayTile

# from create_indoor_mesh import create_mesh_pattern
from mesh_parts.create_tiles import create_mesh_pattern
from mesh_parts.mesh_utils import visualize_mesh

# from mesh_parts.mesh_parts_cfg import FloorPattern, StairsPattern
from pattern_cfg import FloorPattern


def test_wall_mesh(mesh_name="result_mesh.stl"):

    dim = (2.0, 2.0, 2.0)
    cfg = FloorPattern(dim=dim)
    tiles = create_mesh_pattern(cfg)

    wfc_solver = WFCSolver(shape=[24, 24], dimensions=2, seed=None)

    for tile in tiles.values():
        print(tile)
        wfc_solver.register_tile(*tile.get_dict_tile())

    # init_args = {"idx": [wfc_solver.shape[0] // 2, wfc_solver.shape[1] // 2], "tile_name": "floor"}
    init_tiles = [
        ("floor", (wfc_solver.shape[0] // 2, wfc_solver.shape[1] // 2)),
        # ("floor", [wfc_solver.shape[0] // 4, wfc_solver.shape[1] // 4]),
        # ("floor", [wfc_solver.shape[0] // 4, 3 * wfc_solver.shape[1] // 4]),
        # ("platform_1111_f", [3 * wfc_solver.shape[0] // 4, wfc_solver.shape[1] // 4]),
        # ("platform_2222_f", [3 * wfc_solver.shape[0] // 4, 3 * wfc_solver.shape[1] // 4]),
    ]
    # init_args = {"idx": [wfc_solver.shape[0] // 2, wfc_solver.shape[1] // 2], "tile_name": "platform_2222"}
    try:
        wave = wfc_solver.run(init_tiles=init_tiles, max_steps=10000)
    except Exception as e:
        print("Exception ", e)
        return
    # wave = wfc_solver.run()
    # tile_arrays = {}
    # for tile in tiles.values():
    #     tile_arrays[tile.name] = tile.get_array()

    tile_array = tiles["floor"].get_array()
    array_shape = tile_array.shape
    img = np.zeros((wave.shape[0] * array_shape[0], wave.shape[1] * array_shape[1]))
    for y in range(wave.shape[0]):
        for x in range(wave.shape[1]):
            # tile = tile_arrays[wfc_solver.names[wave[y, x]]]
            tile = tiles[wfc_solver.names[wave[y, x]]].get_array()
            img[y * array_shape[0] : (y + 1) * array_shape[0], x * array_shape[1] : (x + 1) * array_shape[1]] = tile

    # plt.imshow(img)
    # plt.colorbar()
    # plt.show()

    names = wfc_solver.names

    result_mesh = trimesh.Trimesh()
    for y in range(wave.shape[0]):
        for x in range(wave.shape[1]):
            # print("name ", names[wave[y, x]], x, y)
            # mesh = meshes.get_mesh(names[wave[y, x]])
            # print("mesh ", tiles[names[wave[y, x]]])
            mesh = tiles[names[wave[y, x]]].get_mesh().copy()
            # print("array ", tiles[names[wave[y, x]]].get_array())
            # mesh.show()
            xy_offset = np.array([x * dim[0], -y * dim[1], 0.0])
            mesh.apply_translation(xy_offset)
            result_mesh += mesh

    result_mesh.export(mesh_name)
    visualize_mesh(result_mesh)
    # result_mesh.show()


if __name__ == "__main__":
    for i in range(1):
        name = f"results/result_mesh_{i}.stl"
        test_wall_mesh(name)
