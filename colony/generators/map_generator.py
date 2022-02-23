"""All types of map generators are defined here.
"""
import abc
from colony.configuration import WorldSetup
import numpy as np


class MapGenerator(abc):
    """Abstract class for map generator.
    """
    @abc.abstractclassmethod
    def get_bitmap(self):
        """Return the bitmap of generated map.
        """
        pass


class GreenMapGenerator(MapGenerator):
    """Generator for grass-based map.
    """
    def __init__(self, seed: int = None, world_cfg: WorldSetup = WorldSetup()):
        """
        Args
            seed: seed for this generator.
            world_cfg: use this pointer to access world infomration like size.

        """
        self.rng = np.random.RandomState(seed)
        self.map = np.full(shape=(world_cfg.width, world_cfg.height), fill_value=101)


        return

    def get_bitmap(self):
        """Return the bitmap of generated map.
        """
        return self.map