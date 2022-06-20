"""Loads image assets from the disk and perform necessary processing.
"""
import os
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path

import cv2

asset_path = Path(__file__).parent.joinpath("assets")

@dataclass
class AssetMeta:
    
    pass


class ImageLoader:

    def perform_image_check(self, image: np.ndarray):
        pass

    def cut_into_smaller_pieces(self, large_image: np.ndarray, ref: AssetMeta):
        pass

    def load_from_disk(self, tileset_name: str):
        pass
    
    def get_raw_single(self, tile_name: str):
        pass

    def get_raw_batch(self):
        pass