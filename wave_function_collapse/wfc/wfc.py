from ctypes import Array
import random
from threading import local
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
from typing import Literal, Tuple, Dict
import itertools
import copy


class Wave:
    def __init__(self, n_tiles: int, shape: list, dimensions: int = 2):
        self.n_tiles = n_tiles
        self.shape = shape
        self.dimensions = dimensions
        self.wave = np.zeros(shape, dtype=np.int32)  # first dimension is for the tile, second is for the orientation
        self.valid = np.ones((self.n_tiles, *shape), dtype=bool)
        self.is_collapsed = np.zeros(shape, dtype=bool)

    def substitute(self, obj: "Wave"):
        self.wave = copy.deepcopy(obj.wave)
        self.valid = copy.deepcopy(obj.valid)
        self.is_collapsed = copy.deepcopy(obj.is_collapsed)

    def copy(self):
        new_wave = Wave(self.n_tiles, self.shape, self.dimensions)
        new_wave.wave = copy.deepcopy(self.wave)
        new_wave.valid = copy.deepcopy(self.valid)
        new_wave.is_collapsed = copy.deepcopy(self.is_collapsed)
        return new_wave


class WFCCore:
    """Wave Function Collapse algorithm implementation."""

    def __init__(self, n_tiles: int, connections: dict, shape: list, dimensions: int = 2):
        """Initialize the WFC algorithm.
        Args:
            n_tiles: number of tiles
            connections: dictionary of connections for each tile
            shape: shape of the wave
            dimensions: number of dimensions of the wave
        """

        self.n_tiles = n_tiles
        self.connections = connections
        self.shape = shape
        self.dimensions = dimensions
        self.new_idx = None
        self.wave = Wave(n_tiles, shape, dimensions)
        self.history = []
        self.back_track_cnt = 0
        self.prev_remaining_grid_num = np.sum(self.wave.is_collapsed == False)
        self.total_back_track_cnt = 0

    def _get_neighbours(self, idx):
        """Get the neighbours of a given tile."""
        neighbours = np.tile(idx, (2 * self.dimensions, 1))
        d_idx = np.vstack([np.eye(self.dimensions, dtype=int), -np.eye(self.dimensions, dtype=int)])
        neighbours += d_idx
        # Remove out of bounds neighbours
        neighbours = neighbours[np.all(neighbours >= 0, axis=1) & np.all(neighbours < self.shape, axis=1)]
        directions = neighbours - idx
        return neighbours, directions

    def _get_possible_tiles(self, tile_id, directions):
        """Get the constraints of a given tile.
        Based on the tile's connections and the directions of the neighbours."""
        possible_tiles = []
        for direction in directions:
            d = tuple(direction)
            possible_tiles.append(self.connections[tile_id][d])
        return possible_tiles

    def _update_wave(self, idx: np.ndarray, tile_id: int):
        self.wave.wave[tuple(idx)] = tile_id
        self.wave.is_collapsed[tuple(idx)] = True
        self.wave.valid[(slice(None),) + tuple(idx)] = False
        self.wave.valid[(tile_id,) + tuple(idx)] = True
        self._update_validity(idx, tile_id)

    def _update_validity(self, new_idx: np.ndarray, tile_id: int):
        neighbours, directions = self._get_neighbours(new_idx)
        possible_tiles = self._get_possible_tiles(tile_id, directions)
        non_possible_tiles = [np.setdiff1d(np.arange(self.n_tiles), pt) for pt in possible_tiles]
        for neighbor, tiles in zip(neighbours, non_possible_tiles):
            self.wave.valid[(tiles,) + tuple(neighbor)] = False

    def _random_collapse(self, entropy):
        """Choose the indices of the tiles to be observed."""
        indices = np.argwhere(entropy == np.min(entropy))
        return np.array(random.choice(indices))

    def collapse(self, entropy):
        """Collapse the wave."""
        # Choose a tile with lowest entropy. If there are multiple, choose randomly.
        return self._random_collapse(entropy)

    def init_randomly(self):
        """Initialize the wave randomly."""
        idx = np.random.randint(0, self.shape, self.dimensions)
        tile_id = np.random.randint(0, self.n_tiles)
        self._update_wave(idx, tile_id)
        self.new_idx = idx

    def init(self, idx, tile_id):
        self._update_wave(idx, tile_id)
        self.new_idx = idx
        print("wave ", self.wave.wave)

    def observe(self, idx):
        """Observe a tile."""
        tile_id = np.random.choice(np.arange(self.n_tiles)[self.wave.valid[(slice(None),) + tuple(idx)]])
        self._update_wave(idx, tile_id)

    def solve(self):
        """Solve the WFC problem."""
        # self.update_history()
        while True:
            # Find a tile with lowest entropy
            entropy = np.sum(self.wave.valid, axis=0)
            entropy[self.wave.is_collapsed] = self.n_tiles + 1
            idx = self.collapse(entropy)
            # print("Entropy:\n", entropy)
            # print("wave:\n", self.wave.wave)
            if entropy[tuple(idx)] == self.n_tiles + 1:
                break
            if entropy[tuple(idx)] == 0:
                self._back_track()
                continue
            else:
                if (
                    np.sum(self.wave.is_collapsed == False) < self.prev_remaining_grid_num
                    or np.sum(self.wave.is_collapsed == False) == 1
                ):
                    # print("prev_remaining_grid_num: ", self.prev_remaining_grid_num)
                    # self.prev_remaining_grid_num = min(
                    #     self.prev_remaining_grid_num, np.sum(self.wave.is_collapsed == False)
                    # )
                    self.prev_remaining_grid_num = np.sum(self.wave.is_collapsed == False)
                    self.back_track_cnt = 0
                    self.update_history()
                self.observe(idx)

            # print("wave ", self.history[0].is_collapsed)
            # break

        return self.wave.wave

    def update_history(self):
        self.history.append(self.wave.copy())

    def _back_track(self):
        """Backtrack the wave."""
        # self.prev_remaining_grid_num = np.sum(self.wave.is_collapsed == False)
        self.back_track_cnt += 1
        self.total_back_track_cnt += 1
        look_back = min(self.back_track_cnt // 10, len(self.history) - 1)
        # if self.total_back_track_cnt > 1000:
        #     look_back += min(self.total_back_track_cnt // 1000, len(self.history))
        # print("look_back:", self.total_back_track_cnt, look_back, self.prev_remaining_grid_num, len(self.history))
        # if self.back_track_cnt > len(self.history) * 10:
        #     raise ValueError("Too many backtracks.", self.back_track_cnt, len(self.history))
        if self.total_back_track_cnt > 100000:
            raise ValueError("Too many total backtracks.", self.total_back_track_cnt)
        self.wave = self.history[-1 - look_back].copy()
        if look_back == len(self.history) - 1:
            # print("wave ", self.wave.is_collapsed)
            entropy = np.sum(self.wave.valid, axis=0)
            # print("Entropy:\n", entropy)


@dataclass
class Direction2D:
    """2D directions"""

    up: tuple = (-1, 0)
    left: tuple = (0, -1)
    down: tuple = (1, 0)
    right: tuple = (0, 1)
    base_directions: tuple = ("up", "left", "down", "right")

    def __post_init__(self):
        self.directions: Dict[int, str] = {
            0: self.base_directions,
            90: tuple(np.roll(np.array(self.base_directions), -1)),
            180: tuple(np.roll(np.array(self.base_directions), -2)),
            270: tuple(np.roll(np.array(self.base_directions), -3)),
        }
        self.flipped_directions: Dict[str, tuple] = {
            "x": tuple(np.array(self.base_directions)[[2, 1, 0, 3]]),
            "y": tuple(np.array(self.base_directions)[[0, 3, 2, 1]]),
        }
        self.is_edge_flipped: Dict[str, tuple] = {
            "x": ("left", "right"),
            "y": ("up", "down"),
            # "y": ("left", "right"),
            # "x": ("up", "down"),
        }


@dataclass
class Direction3D:
    """3D directions"""

    up: tuple = (0, 0, 1)
    down: tuple = (0, 0, -1)
    front: tuple = (-1, 0, 0)
    left: tuple = (0, -1, 0)
    back: tuple = (1, 0, 0)
    right: tuple = (0, 1, 0)
    base_directions: tuple = ("up", "down", "front", "left", "back", "right")

    def __post_init__(self):
        self.directions: dict = {
            0: self.base_directions,
            90: self.base_directions[:2] + tuple(np.roll(np.array(self.base_directions[2:]), -1)),
            180: self.base_directions[:2] + tuple(np.roll(np.array(self.base_directions[2:]), -2)),
            270: self.base_directions[:2] + tuple(np.roll(np.array(self.base_directions[2:]), -3)),
        }
        self.flipped_directions: dict = {
            "x": tuple(np.array(self.base_directions)[[0, 1, 2, 5, 4, 3]]),
            "y": tuple(np.array(self.base_directions)[[0, 1, 4, 3, 2, 5]]),
            "z": tuple(np.array(self.base_directions)[[1, 0, 2, 3, 4, 5]]),
        }
        self.is_edge_flipped: dict = {
            "x": ("front", "back", "up", "down"),
            "y": ("left", "right", "up", "down"),
            "z": ("left", "right", "front", "back"),
        }


class Edge(object):
    """class to handle edges"""

    def __init__(self, dimension=2, edge_types: Dict[str, str] = {}):
        """Initialize the edge class.
        Args:
            edge_types: dictionary of edge types. ex. {"up": "edge_name_up", "down": "edge_name_down", ...}
            dimension: dimension of the wave
        """
        self.dimension = dimension
        if dimension == 2:
            self.directions = Direction2D()
        elif dimension == 3:
            self.directions = Direction3D()
        else:
            raise ValueError("Dimension must be 2 or 3.")
        if len(edge_types) > 0:
            self.register_edge_types(edge_types)

    def register_edge_types(self, edge_types: Dict[str, str]):
        """Register edge types."""
        self._check_edge_types(edge_types)
        self.edge_types = edge_types

    def _direction_to_tuple(self, direction):
        return getattr(self.directions, direction)

    def to_str(self, direction):
        for k, v in self.directions.__dict__.items():
            if v == direction:
                return k

    def _check_edge_types(self, edge_types):
        for key in self.directions.base_directions:
            if key not in edge_types:
                raise ValueError(f"Edge type {key} is not defined.")

    # def get_rotated_edge(self, deg):
    #     if deg not in self.directions.directions:
    #         raise ValueError(f"Rotation degree {deg} is not defined.")
    #     basic_directions = self.directions.directions[0]
    #     new_directions = self.directions.directions[deg]
    #     return {new_key: self.edge_types[key] for new_key, key in zip(new_directions, basic_directions)}

    def get_tuple_edge_types(self):
        return {self._direction_to_tuple(key): value for key, value in self.edge_types.items()}

    def to_tuple(self, edge_types):
        return {self._direction_to_tuple(key): value for key, value in edge_types.items()}


class ConnectionManager:
    """Class to manage the connections between tiles."""

    def __init__(self, dimension=2):
        self.connections = {}
        self.names = []
        self.edge_types_of_tiles = {}  # dict of edges. key: tile_name, value: dict of edges
        self.all_tiles_of_edge_type = {}  # dict of edges for each tile key: edge_type, value: (direction, tile_name)
        self.dimension = dimension
        self.edge_def = Edge(edge_types=self.edge_types_of_tiles)

    def register_tile(
        self,
        name: str,
        edge_types: dict,
    ):

        edges = Edge(edge_types=edge_types, dimension=self.dimension)

        self._register_tile(name, edges.get_tuple_edge_types())

    def _register_tile(self, name: str, edge_types: Dict[tuple, str]):
        """Register a tile with the connection manager.
        Args:
            name: Name of the tile.
            edge_types: Dict of edges. key: direction in tuple, value: edge_type
        """
        self.names.append(name)
        self.edge_types_of_tiles[name] = edge_types
        for direction, edge in edge_types.items():
            if edge not in self.all_tiles_of_edge_type:
                self.all_tiles_of_edge_type[edge] = []
            self.all_tiles_of_edge_type[edge].append((direction, name))

    def compute_connection_dict(self):
        connections = {}
        readable_connections = {}
        for name in self.names:
            edge_types = self.edge_types_of_tiles[name]
            local_connections = {}
            local_readable_connections = {}
            for direction_1, edge_type in edge_types.items():
                local_connections[direction_1] = set()
                local_readable_connections[self.edge_def.to_str(direction_1)] = set()
                another_edge_type = edge_type[::-1]
                for direction_2, name_2 in self.all_tiles_of_edge_type[another_edge_type]:
                    if (np.array(direction_1) + np.array(direction_2) == 0).all():
                        local_connections[direction_1].add(name_2)
                        local_readable_connections[self.edge_def.to_str(direction_1)].add(name_2)
            connections[name] = local_connections
            readable_connections[name] = local_readable_connections
        self.readable_connections = readable_connections
        return self._replace_name_with_number(connections)

    def _replace_name_with_number(self, d: dict):
        """Replace the names of the tiles with numbers. Recursively."""
        # if there are string which is in self.names, replace it with the index of self.names
        new_d = {}
        for key, value in d.items():
            if isinstance(key, str) and key in self.names:
                new_d[self.names.index(key)] = value
            else:
                new_d[key] = value
        d = new_d
        for key, value in d.items():
            if isinstance(value, dict):
                d[key] = self._replace_name_with_number(value)
            elif isinstance(value, str):
                if value in self.names:
                    d[key] = self.names.index(value)
            elif isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
                value = list(value)
                for i, item in enumerate(value):
                    if isinstance(item, str):
                        if item in self.names:
                            value[i] = self.names.index(item)
                d[key] = tuple(sorted(value))
            else:
                print("type of value ", type(value))
                raise ValueError("Unknown type in the connection dict.")
        return d


class WFCSolver(object):
    """Class to solve the WFC problem."""

    def __init__(self, shape, dimensions, seed=None):
        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)
        self.cm = ConnectionManager(dimension=dimensions)
        self.shape = shape
        self.dimensions = dimensions

    def register_tile(self, name, edge_types):
        self.cm.register_tile(name, edge_types)

    def run(self, init_args={}):
        connections = self.cm.compute_connection_dict()
        wfc = WFCCore(len(self.cm.names), connections, self.shape, self.dimensions)
        print("Start solving...")
        if len(init_args) > 0:
            print("init ", init_args)
            idx = self.cm.names.index(init_args["tile_name"])
            print("idx ", idx)
            wfc.init(init_args["idx"], idx)
        else:
            wfc.init_randomly()
        wave = wfc.solve()
        return wave

    @property
    def names(self):
        return self.cm.names