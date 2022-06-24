"""Loads image assets from the disk and perform necessary processing.
"""
import os
import numpy as np
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2


ASSET_FOLDER = Path(__file__).parent.joinpath("../assets")


@dataclass
class ImageLoader:
    """
    Attributes
        name: Name of tileset; can be different from its folder name.
        asset_root: Relative path to tileset folder.
        structure: files used for game structural-buildings.
        surface: files used as floor tiles.
        raw_image_set: Points to an ImageSet instance holding raw resolution images.

    """
    name: str
    asset_root: Path
    structure: Dict[str, Dict[str, str]]
    surface: Optional[Dict[str, List[Path]]] = field(default_factory=lambda: {})
    raw_image_set: Dict[str, Dict[str, Dict[str, Any]]] = field(default_factory=lambda: {})

    def __post_init__(self):
        """Formating and check data correctness."""
        assert self.name, "Make sure name is not empty."
        self.asset_root = Path(self.asset_root)
        # load and dump raw image arrays to an ImageSet instance
        for image_name, v in self.structure.items():
            path, sizes = self.unpack_path_size_pair(v)
            images: List[np.ndarray] = self.load_image_from_disk(
                asset_path=path, split=len(sizes)
            )
            self.raw_image_set[image_name] = {
                "images": images,
                "sizes": sizes
            }
        for k, v in self.surface.items():
            self.surface[k] = [Path(p) for p in v]
        
    @staticmethod
    def unpack_path_size_pair(pair: Dict[str, str]) -> Tuple[Path, List[Tuple[int]]]:
        """Unpack image path, sub-image orientation and sizes
        from yaml parser to usable format.
        """
        asset_path: Path = Path(pair['path'])
        size_str: List[str] = pair['sizes'].split(", ")
        asset_sizes: List(Tuple[int, int]) = [
            (int(x[0]), int(x[1])) for x in size_str
        ]
        return asset_path, asset_sizes
    
    def load_image_from_disk(self, asset_path: Path, split: int = 1) -> List[np.ndarray]:
        """Load one image file to memory and perform necessary checks and split.
        """
        image_path: Path = ASSET_FOLDER.joinpath(self.asset_root).joinpath(asset_path)
        assert image_path.is_file(), f"Image file {image_path} not found."
        image: np.ndarray = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
        self.image_check(image)
        
        if split > 1:  # split on x-axis
            images: List[np.ndarray] = np.split(image, split, axis=1)
            return images
        return [image]
        
    @staticmethod
    def image_check(image: np.ndarray):
        """Basic image validation like shape and channel."""
        assert len(image.shape) == 3
        h, w, c = image.shape
        assert c == 4, "Image missing alpha channel."

    def get_imageset(self):
        return self.raw_image_set
