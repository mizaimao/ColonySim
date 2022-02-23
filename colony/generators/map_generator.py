"""All types of map generators are defined here.
"""
import abc
import numpy as np
from configs.map_generator.rule_loader import GreenMapRules, load_rules


class GreenMapGenerator():
    """Generator for grass-based map.
    """
    def __init__(self, seed: int = None, width: int = None, height: int = None):
        """
        Args
            seed: seed for this generator.
            world_cfg: use this pointer to access world infomration like size.

        """
        self.rng = np.random.RandomState(seed)

        # map place holder
        self.map = np.full(shape=(width, height), fill_value=101)
        # load map rules
        self.rules = load_rules("green")


    def get_bitmap(self):
        """Return the bitmap of generated map.
        """
        return self.map
