"""Terrain manager controlling bitmap."""

from typing import Any, Dict, Tuple, List
import numpy as np

from colony.configuration import map_cfg


class TerrainManager:
    """Manages terrian."""
    def __init__(self, bitmap: np.ndarray = map_cfg.bitmap):
        """Init"""
        self.bitmap: np.ndarray = bitmap
        self.height, self.width = self.bitmap.shape
    