"""Intermediate interface connecting plotting modules and assets on disk.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import cv2

from colony.utils.image_loader import ImageLoader, ImageSet



class ImageManager:

    def __init__(self, seed: int = 720):

        # stores images in various resolutions; key is zoom multiplier; -1 means raw
        self.cache: Dict[str, ImageSet] = {}

        self.loader: ImageLoader = ImageLoader()
        self.rng = np.random.RandomState(seed)

    def cache_raw_set(self, set_name: str):
        pass

    def get_raw(self, set_name: str):
        pass

    def get_image(self, item_name: str):
        pass

