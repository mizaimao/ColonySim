"""Building objects for colony."""
from curses import termattrs
from dataclasses import dataclass, field
from distutils.command.build import build
from tkinter import BitmapImage
from typing import Any, List, Dict, Set, Tuple, Optional
from matplotlib.style import available

import numpy as np

from colony.configuration import res_cfg
from colony.utils.image_manager import ImageManager
from colony.utils.cooridinate_helper import LocationFinder
from colony.characters.terrain import TerrainManager
from colony.configs.map_generator.ref import BUILDABLE

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
        terrain_man: TerrainManager,
        combined_step: Dict[Tuple[int, int], Any],
        image_manager: ImageManager = None,
        seed: int = 720,
    ):
        self.terrain_man: TerrainManager = terrain_man
        # width and height to calculate random locations
        self.height, self.width = self.terrain_man.bitmap.shape
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
        # rng for random locations, orientations, etc.
        self.rng: np.random.RandomState = np.random.RandomState(seed)
        # random location builder, refactored part from this class
        self.finder: LocationFinder = LocationFinder(terrain_man=terrain_man,rng=self.rng)

    def update_combined_step(self, combined_step: Dict[Tuple[int, int], Any]):
        """Should be called at the end of each iteration, such that building manager can
        get up-to-date information of current tile info."""
        self.combined_step = combined_step

    def progress_building_step(self):
        pass
        

    def add_building_non_image(self, building_type: int):
        pass

    
    def add_building(
            self,
            type: int,
            loc: Tuple[int, int] = None,
            tech: int = 0,
            orientation: int = None,
        ) -> bool:
        """
        Do checks and build the building if we can. We check resources first because
        that's computationally cheaper than physical checks.
        1. Resource checks: if storage can support such a building.
        2. Physical checks: if given location and orientation will have free tiles;
        If checks passed, then build it and deduct resources from colony.

        There are cases when location or orientation not specified:
        1. If neither were given, then chose a random location and random orientation.
        2. If only location was given, then check all possible orientations and
            randomly select one.
        3. If only orientation was given, then choose a random location (or keep trying
            until all tiles are exhauseted)
        """
        if orientation is not None:
            assert orientation >= 0, "Orientation should be a non-negative integer; or \
                None for a random orientation."

        # do resource/financial checks
        required_res: Dict[int, int] = res_cfg[type][tech]
        


        # resource check passed, and check locations
        # get list of available orientations:
        avail_ori: List[Tuple[int, int]] = self.image_manager.sizes[type]

        # two key variables for building
        buildable_loc: Tuple[int, int] = None
        buildbale_ort: int = -1  # -1 for invalid

        # case 0: when both loc and orientation are given
        if (loc is not None) and (orientation is not None):
            if self.finder.validate_loc_and_ori(loc, avail_ori[orientation]):
                buildable_loc = loc
                buildbale_ort = avail_ori[orientation]
        # case 1: neither were given
        elif loc is None:
            if orientation is None:
                buildable_loc, buildbale_ort = \
                    self.finder.build_with_random_loc_and_random_ori(avail_ori=avail_ori)
            # case 3: only orientation was given
            else:
                buildable_loc = \
                    self.finder.build_with_random_loc_and_given_ori(size=avail_ori[orientation])
                buildbale_ort = orientation
        # case 2: only location was given
        else:
            buildable_loc = loc
            buildbale_ort = self.finder.build_at_location_with_random_orientation(
                loc=loc, sizes=avail_ori
            )
        # now we check if building location and orientation are valid
        if (buildable_loc is None) or (buildbale_ort == -1):
            return False

        # flow reaches here if physical check passed
        # both checks passed, therefore we build it
        # enumerate building id
        new_building_id: int = self.building_id
        self.building_id += 1

        if self.image_manager is None:
            self.add_building_non_image(building_id=new_building_id)
        if orientation is None:
            orientation = 0

        new_building: Building = Building(
            id=id, type=type, location=buildable_loc, tech=tech, orientation=buildbale_ort
        )
        self.buildings[id] = new_building
        return True

    def relocate_building(self, id: int) -> bool:
        """Relocate building with given id to a new place. Returns if it will be successful.
        """
        pass

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
