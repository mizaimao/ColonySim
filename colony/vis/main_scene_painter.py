"""Helps drawing main scene.
"""
import numpy as np
from typing import Any, Callable, Dict, List, Tuple, Union

from colony.configs.map_generator.ref import map_ref, STRUCTURE_PREFIX
from colony.characters.colony import Colony
from colony.characters.spore import Spore
from colony.characters.buildings import Building
from colony.utils.image_manager import ImageManager
from colony.vis.colony_viewers_basic import ColonyView, ColonyView2D
from colony.vis.colony_viewers import ColonyViewIso, ColonyViewIsoImage


# color of players in BGR
#color_dict: Dict[int, Tuple[int, ...]] = {1: (245, 158, 66), 3: (95, 95, 250)}
TILE_OUTLINE: bool = True

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
            self.colony.terrain_man.width,
            self.colony.terrain_man.height,
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
        # merge building step and spore step
        building_step: Dict[Tuple[int, int], Building] = self.colony.building_man.building_step
        spore_step: Dict[Tuple[int, int], int] = self.colony.step
        # value be differnt types of objects, like Building, Spore, etc.
        merged_step: Dict[Tuple[int, int], Any] = {}

        for coor, building in building_step.items():
            if coor in merged_step:
                raise ValueError(f"Merged step show repitive builiding at {coor}.")
            merged_step[coor] = building
        for coor, spore_ids in spore_step.items():
            if coor not in merged_step:
                merged_step[coor] = self.colony.spore_man.spores[spore_ids[0]]  # the top spore
            else:  # this tile is occupied by another building/spore already
                pass

        # need to sort spores to paint them in a correct order, this is needed for isometrci viewing
        _tempList = sorted(merged_step.keys(), key=lambda x: x[0], reverse=True)
        step_sorted: list = sorted(_tempList, key=lambda x: x[1])
        # paint all objects
        for (x, y) in step_sorted:
            obj_on_tile = merged_step[(x, y)]
            if isinstance(obj_on_tile, Spore):
                spore_color = map_ref[obj_on_tile.sex][-1]
                self.painter.paint_large_pixel(frame, x, y, spore_color, outline=TILE_OUTLINE)
            elif isinstance(obj_on_tile, Building):
                building_code: int = STRUCTURE_PREFIX * 1000 + obj_on_tile.type * 10 + obj_on_tile.tech_level
                building_color = map_ref[building_code][-1]
                self.painter.paint_large_pixel(
                    frame, x, y, building_color, size=obj_on_tile.size, outline=TILE_OUTLINE
                )

        return frame
