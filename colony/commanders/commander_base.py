"""Input interface to Colony instances.
"""
import cv2
from typing import Dict, List, Tuple, Union

from colony.configuration import res_cfg
from colony.characters.colony import Colony
from colony.characters.colony_stats import HappinessManager, ColonyResourceManager
from colony.characters.buildings import Building, ColonyBuildingManager
from colony.characters.terrain import TerrainManager
from colony.characters.spore import Spore, ColonySporeManager
from colony.utils.image_manager import ImageManager
from colony.utils.cooridinate_helper import bfs


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

    def perform_resource_check(self, res_required: Dict[int, int]) -> bool:
        """Check if colonly's storage can cover all resource requirements
        parsed in the argeument."""
        for res_type, amount in res_required.items():
            if self.res_man.storage.res[res_type] < amount:
                return False
        return True

    def consume_resource(self, res_required: Dict[int, int]):
        """Remoce resources from colony storage.
        Should be coupled with "perform_resource_check()"."""
        for res_type, amount in res_required.items():
            self.res_man.storage.res[res_type] -= amount

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
        assert level > 0, "Tech level should be larger than 0."
        res_required: Dict[int, int] = res_cfg.building_costs[structure_type][level]
        # perform resource check
        if not self.perform_resource_check(res_required=res_required):
            print('Building, res check failed')
            return
        # resource check passed, now get building id
        building_id: int = self.building_man.check_building_is_buildable(
            type=structure_type, loc=location, tech=level, orientation=orientation
        )
        # building physical check didn't pass, therefore not buildable
        if building_id == -1:
            print("Building, loc check failed")
            return
        # remove resource from colony storage and modify terrain to finish construction
        self.consume_resource(res_required=res_required)
        building: Building = self.building_man.buildings[building_id]
        self.terrain_man.add_building(
            start=building.location,
            size=building.size,
            building_type=structure_type,
            tech=level,
        )

    def move_spore(
        self,
        spore_id: Union[int, List[int]],
        dest: Tuple[int, int],
    ):
        """Command a spore to move to a new location.
        This command will override spores' current routes.
        """
        # pointer to spore
        spore: Spore = self.spore_man[spore_id]

        # calculate route to destination
        route: List[Tuple[int, int]] = bfs(
            self.terrain_man.bitmap,
            start=spore.pos,
            end=dest,
            step=self.colony.step,
            diagonal_move=False,
            spore_overlapping=False
            )
        if not route:  # empty route
            return False
        spore.route = route
        return True
