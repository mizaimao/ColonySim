"""Helps drawing main scene.
"""
import numpy as np
from typing import Callable, Dict, List, Tuple, Union

from colony.characters.colony import Colony
from colony.utils.image_manager import ImageManager
from colony.vis.colony_viewers_basic import ColonyView, ColonyView2D
from colony.vis.colony_viewers import ColonyViewIso, ColonyViewIsoImage

# color of players in BGR
color_dict: Dict[int, Tuple[int, ...]] = {1: (245, 158, 66), 3: (95, 95, 250)}

available_painters: Dict[str, ColonyView] = {
    "2D": ColonyView2D,
    "isometric": ColonyViewIso,
    "isometric_image": ColonyViewIsoImage
}

class MainScenePainter:
    def __init__(self, style: str, colony: Colony, bitmap: np.ndarray, width: int, height: int, image_manager: ImageManager):
        self.colony: Colony = colony
        self.bitmap: np.ndarray = bitmap

        # check and setup painter
        assert style in available_painters, f"{style} not supported."
        painter_class = available_painters[style]
        self.painter = painter_class(
            self.colony.width,
            self.colony.height,
            width,
            height,
            bitmap=self.bitmap,
            image_manager=image_manager
        )

        self.static_frame = self.painter.get_static_frame()
        self.painter.paint_playground()

    def paint_main_scence(self) -> np.ndarray:
        # make a copy of raw background
        frame = self.static_frame.copy()
        # need to sort spores to paint them in a correct order, this is needed for isometrci viewing
        _tempList = sorted(self.colony.step.keys(), key=lambda x: x[0], reverse=True)
        step_sorted = sorted(_tempList, key=lambda x: x[1])
        # paint all spores
        for (x, y) in step_sorted:
            spores = self.colony.step[(x, y)]
            # show only the first spore
            top_spore = self.colony.spore_man.spores[spores[0]]
            # dye this block
            splore_color = color_dict[top_spore.sex]
            self.painter.paint_large_pixel(frame, x, y, splore_color, outline=False)

        return frame
