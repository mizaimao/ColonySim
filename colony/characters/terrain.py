"""Terrain manager controlling bitmap."""

from typing import Any, Dict, Tuple, List
import numpy as np

from colony.configuration import map_cfg
from colony.configs.map_generator.ref import STRUCTURE_PREFIX


class TerrainManager:
    """Manages terrian."""

    def __init__(self, bitmap: np.ndarray = map_cfg.bitmap):
        """Init"""
        # make a copy of raw map, in case there is a need to revert something
        self.original_bitmap: np.ndarray = bitmap.copy()
        self.bitmap: np.ndarray = bitmap
        self.height, self.width = self.bitmap.shape

        print("chicken")
        self.bitmap_override()
        print("chicken done")

    def bitmap_override(self):
        """Debugging function to forcefully modify the bitmap."""
        magic_size: int = 7
        self.bitmap[0: magic_size, 0: magic_size] = 301
        self.bitmap[-magic_size: , -magic_size: ] = 7110
        self.bitmap[-magic_size: , 0: magic_size] = 7210
        self.bitmap[0: magic_size, -magic_size: ] = 111


    def add_building(
        self,
        start: Tuple[int, int],
        size: Tuple[int, int],
        building_type: int,
        tech: int,
    ):
        """Add building to bitmap. The bitmap is read directly by visulaizer to draw stuff
        on screen, and in this function we modify tiles that the building occupies to codes
        that visualizer can recognize.
        1. The upper left tile will be the drawing tile.
        2. If a building occupies more than one tile, then only the drawing tile has the code
            that visualizer would use, and other tiles would have codes with a zero as postfix
            such that the visualizer would ignore.
        3. Building codes are related to codes recognized by visualizer but a bit different:
            e.g. a building may have code 21, and the drawing code could be 7223 and 7220,
            where 7 is prefix of building, and 3 means tech level is 3; or 0 means it's just
            occupied by this building but visualizer should not draw anything on this tile.

        Args
            start: upper left tile of building, also the tile to draw the building in visualizer.
            size: size in terms of how many tiles it occupies on x and y directions.
            building_type: code for building, like 11, 21, 22, 23, etc.
            tech: tech level of building.
        """
        x, y = start
        building_code: int = STRUCTURE_PREFIX * 1000 + building_type * 10
        for x_extend in range(size[0]):
            for y_extend in range(size[1]):
                if x_extend == 0 and y_extend == 0:
                    self.bitmap[y][x] = building_code + tech
                else:
                    self.bitmap[y + y_extend][x + x_extend] = building_code
