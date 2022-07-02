"""Input interface to Colony instances.
"""
import cv2
from typing import Dict, List, Tuple

from colony.configuration import res_cfg
from colony.characters.colony import Colony
from colony.characters.colony_stats import HappinessManager, ColonyResourceManager
from colony.characters.buildings import ColonyBuildingManager
from colony.characters.terrain import TerrainManager
from colony.characters.spore import Spore, ColonySporeManager
from colony.utils.image_manager import ImageManager


class ColonyCommander:
    """Interface to issue commands to a Colony instance. Many of functions are wrappers to existing
    functions that reside in different sub-modules of the colony instance."""

    def __init__(self, colony: Colony):
        # setup pointers to manger classes
        self.colony: Colony = colony
        self.terrain_man: TerrainManager = colony.terrain_man
        self.image_manager: ImageManager = colony.image_manager
        self.spore_man: ColonySporeManager = colony.spore_man
        self.happiness_man: HappinessManager = colony.happiness_man
        self.building_man: ColonyBuildingManager = colony.building_man
        self.res_man: ColonyResourceManager = colony.res_man

    def build_structure(
        self,
        structure_type: int,
        level: int,
        location: Tuple[int, int] = None,
        orientation: int = None,
    ):
        """Add structure to bitmap.

        Args
            structure_type: structure code, each code represents a type of sctructure.
            level: level of structure to build.
            location: location to build. If not supplied, a random location will be used.
            orientation: orientation of the sctructure. If not supplied, use random.
        """
        res_required: Dict[int, int] = res_cfg.building_costs[structure_type][level]
        # perform resource check

        pass
