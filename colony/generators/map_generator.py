"""All types of map generators are defined here.
"""
import numpy as np

class GreenMapGenerator:
    """
    """
    def __init__(self, seed: int = None):
        self.rng = np.random.RandomState(seed)

        return

    def get_bitmap(self):
        return