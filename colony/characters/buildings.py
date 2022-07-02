"""Building objects for colony."""
from curses import termattrs
from dataclasses import dataclass, field
from distutils.command.build import build
from typing import Any, List, Dict, Set, Tuple, Optional

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
    type: int
    tech_level: int
    location: Tuple[int, int]
    orientation: Optional[int] = 0
    size: Optional[Tuple[int, int]] = field(default_factory=lambda: (1, 1))


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
        self.building_id: int = 0
        # colony building locations
        self.building_step: Dict[Tuple[int, int], Building] = {}
        # rng for random locations, orientations, etc.
        self.rng: np.random.RandomState = np.random.RandomState(seed)
        # random location builder, refactored part from this class
        self.finder: LocationFinder = LocationFinder(
            terrain_man=terrain_man, rng=self.rng
        )

    def update_combined_step(self, combined_step: Dict[Tuple[int, int], Any]):
        """Should be called at the end of each iteration, such that building manager can
        get up-to-date information of current tile info."""
        self.combined_step = combined_step

    def progress_building_step(self):
        pass

    def add_building_non_image(self, building_type: int):
        pass

    def check_building_is_buildable(
        self,
        type: int,
        loc: Tuple[int, int] = None,
        tech: int = 1,
        orientation: int = None,
    ) -> int:
        """
        Do checks and build the building if we can. We check resources first because
        that's computationally cheaper than physical checks. Note that resource check
        should already been done by the caller and will not be performed here.
            1. Resource checks: if storage can support such a building. This should
            2. Physical checks: if given location and orientation will have free tiles;
        If checks passed, then add the building to building manager. Resource is not
        deducted in this step and should be performed elsewhere.
        """
        if orientation is not None:
            assert (
                orientation >= 0
            ), "Orientation should be a non-negative integer; or \
                None for a random orientation."
        avail_ori: List[Tuple[int, int]] = self.image_manager.sizes[type]
        # do physical checks
        buildable_loc, buildbale_ort = self.finder.perform_building_physical_checks(
            loc=loc, orientation=orientation, avail_ori=avail_ori
        )
        if (buildable_loc is None) or (buildbale_ort == -1):
            return -1  # invalid building id, meaning not buildable

        # flow reaches here if both checks passed, therefore we build it
        # enumerate building id
        new_building_id: int = self.building_id
        self.building_id += 1

        if self.image_manager is None:
            self.add_building_non_image(building_id=new_building_id)
        if orientation is None:
            orientation = 0

        new_building: Building = Building(
            id=new_building_id,
            type=type,
            location=buildable_loc,
            tech_level=tech,
            orientation=buildbale_ort,
            size=avail_ori[buildbale_ort],
        )
        self.buildings[new_building_id] = new_building
        self.building_step[buildable_loc] = self.buildings[new_building_id]
        return new_building_id

    def relocate_building(self, id: int) -> bool:
        """Relocate building with given id to a new place. Returns if it will be successful."""
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
