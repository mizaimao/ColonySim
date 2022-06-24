"""Intermediate interface connecting plotting modules and assets on disk.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import yaml

import cv2

from colony.utils.image_loader import ImageLoader, ASSET_FOLDER

AVAILABLE_TILESETS: Dict[str, str] = {
    "space": "Isometric_Space_Colony"
}


def get_tileset_yaml(set_name: str):
    assert set_name in AVAILABLE_TILESETS, f"{set_name} not available."
    yaml_path = ASSET_FOLDER.joinpath(AVAILABLE_TILESETS[set_name] + '.yaml')
    return yaml.safe_load(open(yaml_path))


class ImageManager:
    """Scene painters will communicate with this class to acquire images.
    Also stores cached images of different resolution scales.
    """

    def __init__(self, set_name: str, seed: int = 720):
        """
        Args

            seed: controls random choosing operations (like random orientation of a tile)
        """
        self.seed = seed
        self.rng = np.random.RandomState(seed)

        self.loader: ImageLoader = ImageLoader(**get_tileset_yaml(set_name))

        # stores images in various resolutions; key is zoom multiplier; 0 is raw size
        self.cache: Dict[str, ImageSet] = {0: self.loader.get_imageset}
        

    def load_new_set(self, set_name: str, reset_rng: bool = True):
        """Load a new tileset.
        Not fully implemented"""
        self.loader = ImageLoader(**get_tileset_yaml(set_name))
        if reset_rng:
            self.rng = self.rng(self.seed)
        pass


