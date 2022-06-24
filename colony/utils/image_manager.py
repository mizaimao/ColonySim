"""Intermediate interface connecting plotting modules and assets on disk.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple
import yaml

import cv2

from colony.utils.image_loader import ImageLoader, ASSET_FOLDER

AVAILABLE_TILESETS: Dict[str, str] = {
    "space": "Isometric_Space_Colony"
}
PRESIZING_STEP: float = 0.1


def get_tileset_yaml(set_name: str):
    assert set_name in AVAILABLE_TILESETS, f"{set_name} not available."
    yaml_path = ASSET_FOLDER.joinpath(AVAILABLE_TILESETS[set_name] + '.yaml')
    return yaml.safe_load(open(yaml_path))


class ImageManager:
    """Scene painters will communicate with this class to acquire images.
    Also stores cached images of different resolution scales.
    """

    def __init__(
        self, 
        set_name: str,
        seed: int = 720,
        tile_width: int = 0,
        pre_sizing: Tuple[float, float, float] = [0.8, 2, 0.1]):
        """
        Args
            set_name: Short name of tileset so that it can load assets from disk. 
            seed: Controls random choosing operations (like random orientation of a tile).
            tile_width: Width of a tile in pixel size. Essential for resizing.
            pre_sizing: Pre-caching resized tiles, format is (min, max, step), inclusively
                and step is of 0.1. This may be buggy due to np.arange results.
        """
        print("Loading assets...", end='')
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        # image loader to read images from the disk
        self.loader: ImageLoader = ImageLoader(**get_tileset_yaml(set_name))
        # stores images in various resolutions; key is zoom multiplier; None is raw size
        self.cache: Dict[str, Any] = {None: {}}
        # stores how many x and y mega pixels each image occupies
        self.sizes: Dict[str, List[Tuple(int, int)]] = {}

        self._unpack_raw_tileset()
        self._prescale(tile_width, pre_sizing)
        print('Done')

    def _unpack_raw_tileset(self):
        """Load raw tileset and add their image arrays as well as sizes to internal storage."""
        raw_image_set: Dict[str, Any] = self.loader.get_imageset()
        for tile_name, tile_dict in raw_image_set.items():
            sizes: List[Tuple[int, int]] = tile_dict["sizes"]
            images: List[Tuple[int, int]] = tile_dict["images"]
            self.sizes[tile_name] = sizes
            self.cache[None][tile_name] = images

    def _prescale(self, tile_width: int, re_sizing: Tuple[float, float, float]):
        if tile_width <= 0:
            print("No tile width information, not rescaling...", end='')
            return

        assert len(re_sizing) == 3
        assert re_sizing[0] + re_sizing[2] <= re_sizing[1], f"Invalid rescaling: {re_sizing}."

        for scaling in np.arange(re_sizing[0], re_sizing[1], re_sizing[2]):
            # new size key
            new_size_name: str = "{:.3f}".format(scaling)
            self.rescale_tile_set(new_size_name)

    @staticmethod
    def resize_image_by_width(image: np.ndarray, width: int) -> np.ndarray:
        """Resize image with width while retaining aspect ratio."""
        org_h, org_w, _ = image.shape
        org_ratio: float = org_h / org_w
        return cv2.resize(image, (width, int(width * org_ratio)))

    def load_new_set(self, set_name: str, reset_rng: bool = True):
        """Load a new tileset.
        Not fully implemented"""
        self.loader = ImageLoader(**get_tileset_yaml(set_name))
        if reset_rng:
            self.rng = self.rng(self.seed)
        pass

    def rescale_tile_set(self, scaling: str):
        """Resize tileset to specified size."""
        if scaling in self.cache:  # size already exists
            return
        assert len(scaling) == 5, "Scaling should be 3-position flotas, e.g., \"1.000\"."
        
        # setup new size
        scaling_f: float = float(scaling)
        # setup new scaling dict
        self.cache[scaling] = {}  # Dict[str, List[np.ndarray]]
        # unpack raw image set
        for tile_name, org_images in self.cache[None].items():  # None is key for raw set
            # resize each original tile image
            #org_images: List[np.ndarray] = tile_dict['images']
            new_width: int = int(org_images[0].shape[1] * scaling_f)
            resized: List[np.ndarray] = [
                ImageManager.resize_image_by_width(
                    org_image, new_width) for org_image in org_images
            ]
            self.cache[scaling][tile_name] = resized
