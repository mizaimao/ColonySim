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
    """Load yaml specifing image asset set info, including path, orientations, etc."""
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
        pre_sizing: Tuple[float, float, float] = [0.8, 2, 0.1]):
        """
        The 

        Args
            set_name: Short name of tileset so that it can load assets from disk. 
            seed: Controls random choosing operations (like random orientation of a tile).
            tile_width: Width of a tile in pixel size. Essential for resizing.
            pre_sizing: Pre-caching resized tiles, format is (min, max, step), inclusively
                and step is of 0.1. This may be buggy due to np.arange results.
        """
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self.set_name: str = set_name
        self.tile_width: int = None
        self.pre_sizing: Tuple[float, float, float] = pre_sizing
        # stores images in various resolutions; key mega tile width in px; 0 is raw size
        # other zooming levels will be saved to different keys.
        self.cache: Dict[int, Any] = {0: {}}
        # stores how many x and y mega pixels each image occupies
        self.sizes: Dict[int, List[Tuple(int, int)]] = {}
        # stores names of buildings
        self.building_names: Dict[int, str] = {}

    def prepare_tileset(self, tile_width: int = 0):
        assert self.tile_width is None, "prepare_tileset(tile_width) function should be only executed once."
        self.tile_width = tile_width
        print("Loading assets...", end='')
        # image loader to read images from the disk
        self.loader: ImageLoader = ImageLoader(**get_tileset_yaml(self.set_name))
        self._unpack_raw_tileset()
        self._prescale(self.tile_width, self.pre_sizing)
        print('Done')

    def _unpack_raw_tileset(self):
        """Load raw tileset and add their image arrays as well as sizes to internal storage."""
        raw_image_set: Dict[str, Any] = self.loader.get_imageset()
        for tile_name, tile_dict in raw_image_set.items():
            sizes: List[Tuple[int, int]] = tile_dict["sizes"]
            images: List[Tuple[int, int]] = tile_dict["images"]
            building_name: str = tile_dict["name"]
            self.sizes[tile_name] = sizes
            self.cache[0][tile_name] = images
            self.building_names[tile_name] = building_name

    def _prescale(self, tile_width: int, re_sizing: Tuple[float, float, float]):
        if tile_width <= 0:
            print("No tile width information, not rescaling...", end='')
            return

        assert len(re_sizing) == 3
        assert re_sizing[0] + re_sizing[2] <= re_sizing[1], f"Invalid rescaling: {re_sizing}."

        for scaling in np.arange(re_sizing[0], re_sizing[1], re_sizing[2]):
            # new size key
            target_width: int = int(tile_width  * scaling)
            self.rescale_tile_set(target_width)

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

    def rescale_tile_set(self, target_width: int):
        """Resize tileset to specified size."""
        if target_width in self.cache:  # size already exists
            return
        assert isinstance(target_width, int), f"Use int as width to resize tileset, not {type(target_width)}"
        
        # setup new scaling dict
        self.cache[target_width] = {}  # Dict[int, List[np.ndarray]]
        # unpack raw image set
        for tile_code, org_images in self.cache[0].items():  # 0 is key for raw set
            # resize each original tile image
            resized: List[np.ndarray] = []
            sizes = self.sizes[tile_code]
            for image, size in zip(org_images, sizes):
                new_width: int = int(target_width * (1 + (max(size) - 1) * 0.5))
                resized.append(ImageManager.resize_image_by_width(image, new_width))
            self.cache[target_width][tile_code] = resized

    def get_tile_orientation(self, building_type: int, orientation: int = None):
        """Get tile oirentation. If an orientation is parsed, then check if this orientation is
        available; otherwise, return a random orientation.
        """
        available_orientations: List[Tuple[int, int]] = self.sizes[building_type]
        assert available_orientations, f"Loader error, no orientation was loadded for {building_type}."
        chosen_orientation: int = orientation if (orientation is not None) else \
            self.rng.choice(len(available_orientations))
        assert chosen_orientation < len(available_orientations), "Orientation index out of range."
        size: Tuple[int, int] = available_orientations[chosen_orientation]
        return size
            
    def get_tile_image(self, building_type: int, width: int, index: int = None):
        """Get a tile image by building_type.
        Args
            building_type: Name of tile.
            width: On-screen pixel width of each mega pixel. The function will then return the
                image resized with this width (or generate it first if not cached).
            index: If an index was not given, then a random image from that building_type will be
                returned.
        """
        assert self.tile_width is not None, "Run prepare_tileset(tile_width) first."
        if not width in self.cache:
            self.rescale_tile_set(width)
        
        tile_images: List[np.ndarray] = self.cache[width][building_type]
        image_index: int = index if (index is not None) else self.rng.choice(len(tile_images))
        image_array: np.ndarray = tile_images[image_index]
        image_size: Tuple[int, int] = self.sizes[building_type][image_index]

        return image_array, image_size
