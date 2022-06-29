"""Building objects for colony."""
from dataclasses import dataclass, field
from typing import Any, List, Dict, Tuple, Optional

import numpy as np

from colony.utils.image_manager import ImageManager

TECH_CAP: int = 3


@dataclass
class Building:
    """
    Attributes
        id: unique id of building
        type: type of building, like "stroage", "r11"
        tech_level: current level of building
        location: (x, y) location on bitmap
        orientation: used for visualization, determines index of image assets to draw.
    """

    id: int
    type: str
    tech_level: int
    location: Tuple[int, int]
    orientation: Optional[int] = 0


class ColonyBuildingManager:
    """Manages building objects in a colony."""

    def __init__(
        self,
        width: int,
        height: int,
        combined_step: Dict[Tuple[int, int], Any],
        image_manager: ImageManager = None
    ):
        # width and height to calculate random locations
        self.width: int = width
        self.heigh: int = height
        # imager to retrive building orientation information
        self.image_manager: ImageManager = image_manager
        # colony spore locations
        self.combined_step: Dict[Tuple[int, int], Any] = combined_step

        # building tracking dictionary
        self.buildings: Dict[int, Building] = {}
        # unique building ids
        self.building_id: int = 0,
        # colony building locations
        self.building_step: Dict[Tuple[int, int], Building] = {}

    def update_combined_step(self, combined_step: Dict[Tuple[int, int], Any]):
        """Should be called at the end of each iteration, such that building manager can
        get up-to-date information of current tile info."""
        self.combined_step = combined_step

    def progress_building_step(self):
        pass
        

    def add_building_non_image(self, building_type: int):
        pass

    def validate_loc_and_ori(self, loc: Tuple[int, int], size: Tuple[int, int]) -> bool:
        """Validate whether the building can be built with given location and orientation."""


        return False

    def add_building(
        self,
        type: int,
        loc: Tuple[int, int],
        tech: int = 0,
        orientation: int = None,
    ) -> bool:
        can_be_built: bool = False
        # check if this building can be added
        # get list of available orientations:
        avail_ori: List[Tuple[int, int]] = self.image_manager.sizes[type]
        # parsed orientation, then check this orientation and location
        if orientation is not None:
            can_be_built = self.validate_loc_and_ori(loc, avail_ori[orientation])


        if not can_be_built:
            return False

        # if can be built, then add it
        # enumerate building id
        new_building_id: int = self.building_id
        self.building_id += 1

        if self.image_manager is None:
            self.add_building_non_image(building_id=new_building_id)
        if orientation is None:
            orientation = 0

        new_building: Building = Building(
            id=id, type=type, location=loc, tech=tech, orientation=orientation
        )
        self.buildings[id] = new_building
        return False

    def upgrade_building(self, id: int) -> bool:
        """Upgrade an existing building, returns whether it will be successful."""
        if self.buildings[id].tech_level < TECH_CAP:
            self.buildings[id].tech_level += 1
            return True
        return False

    def downgrade_building(self, id: int) -> bool:
        """Downgrade an existing building, returns whether it will be successful."""
        if self.buildings[id].tech_level > 1:
            self.buildings[id].tech_level -= 1
            return True
        return False

    def demolish_building(self, id: int) -> bool:
        """Remove an existing building, returns whether it will be successful."""
        pass
