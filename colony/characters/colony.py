import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, List


from colony.characters.colony_stats import HappinessManager, ColonyResourceManager
from colony.characters.buildings import ColonyBuildingManager
from colony.characters.terrain import TerrainManager
from colony.characters.spore import Spore, ColonySporeManager
from colony.characters.storage import SporeStorage
from colony.utils.info_manager import InfoManager
from colony.utils.image_manager import ImageManager

STEP_INTERVAL: int = 10

@dataclass
class ColonyGeneralInfo:
    pass


class Colony:
    """
    A colony with width and height, inside multiple individuals will be
    spawned and may encounter each other tirggering potential destruction
    or multiplication.
    """

    def __init__(
        self,
        viewer_width: int = 1440,
        viewer_height: int = 900,
        init_pop: int = 10,
        image_manager: ImageManager = None,
        seed: int = 0,
        verbose: bool = True,
    ):
        """
        Args
            width: width of bitmap
            height: height of bitmap 
            viewer_width: displaying window width in pixel counts
            viewer_height: displaying window height in pixel counts
            init_pop: inital population of this colony
            seed: random seed
            verbose: if true, printing functions in InfoManager will be suppressed
        """
        # settings
        self.viewer_width: int = viewer_width
        self.viewer_height: int = viewer_height
        self.enable_history: bool = False

        # variables
        self.step: Dict[Tuple[int, int], Any] = {}  # coor and objects on it
        self.current_iteration: int = 0
        self.step_record: List[Dict[Tuple[int, int], List[Spore]]] = []  # a record of each step

        # progress variables
        self.tech_stage: int = 0

        # pointers to terrain manager
        self.terrain_man: TerrainManager = TerrainManager()

        # pointers to other managers
        self.info: ColonyGeneralInfo = ColonyGeneralInfo()
        self.image_manager: ImageManager = image_manager
        self.spore_man: ColonySporeManager = ColonySporeManager(
            init_pop=init_pop, terrain_man=self.terrain_man
        )
        self.happiness_man: HappinessManager = HappinessManager(base=15.0)
        self.building_man: ColonyBuildingManager = ColonyBuildingManager(
            terrain_man=self.terrain_man, combined_step=self.step, image_manager=image_manager, seed=seed
        )
        self.res_man: ColonyResourceManager = ColonyResourceManager(
            self.spore_man,
            self.happiness_man,
            self.building_man
        )

        # utilities
        self.rng = np.random.RandomState(seed)
        self.printer: InfoManager = InfoManager(silent_mode=(not verbose))

        
    def check_die_out(self) -> bool:
        """Checks if a colony reaches certerion that do not permit progression.
        For example, if there are less than two individuals alive, then the colony dies out.

        Returns
            bool: true if passes the test and the colony survives.
        """
        # check distinguishing by numbers
        return len(self.spore_man.spores) >= 2

    def calculate_current_step(self):
        """Calculate resource input and output of this step. Spores dead will also be removed.
        Should be called before progressing to the next step.
        Differences are this function computes the current step, while "progress_a_step" projects
        the next iteration.
        """
        if self.current_iteration % STEP_INTERVAL == 0:
            # calculate resource
            self.res_man.progress_res_step()
            # calculate building
            self.building_man.progress_building_step()
            # calculate spore health
            health_list: List[float] = self.spore_man.calculate_spore_health()
            # calculate happiness and expand colony if available
            expansion_ready: bool = self.happiness_man.update(health_list)
            if expansion_ready:
                self.spore_man.expand_if_available()

        # new pop happens before this statement
        spore_step: Dict[Tuple[int, int], List[int]] = self.spore_man.calculate_spore_movements()
        
        new_step = spore_step
        return new_step


    def progress_a_step(self):
        """
        Progress to the next step. We first compuate what happens in the current step, and then
        First, we calculate resource income and consumption;
        Second, we update spore stats (e.g. update their health and location);
        Thrid, merge spore step and building step so that they can be used for visualization

        Returns:
            bool: if the colony dies.
        """
        # calculate the current step, because progression will be based it results of current step
        new_step = self.calculate_current_step()

        # save current step
        if self.enable_history:
            self.step_record.append(self.step.copy())

        if not self.check_die_out():
            self.printer.info("Colony failed, spores unable to reproduce.")
            return False

        self.step = new_step
        self.building_man.update_combined_step(self.step)
        self.current_iteration += 1

        return True
