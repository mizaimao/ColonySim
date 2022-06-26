import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, List


from colony.characters.colony_stats import HappinessManager, ColonyResourceManager
from colony.characters.buildings import ColonyBuildingManager
from colony.characters.spore import Spore, ColonySporeManager
from colony.characters.storage import SporeStorage
from colony.progression.step import *
from colony.utils.info_manager import InfoManager


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
        width: int = 32,
        height: int = 16,
        viewer_width: int = 1440,
        viewer_height: int = 900,
        init_pop: int = 10,
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
        self.width: int = width
        self.height: int = height
        self.viewer_width: int = viewer_width
        self.viewer_height: int = viewer_height
        self.enable_history: bool = False

        # variables
        self.step: Dict[Tuple[int, int], Any] = {}  # coor and objects on it
        self.current_iteration: int = 0
        self.step_record: List[Dict[Tuple[int, int], List[Spore]]] = []  # a record of each step

        # progress variables
        self.tech_stage: int = 0

        # pointers to managers
        self.info: ColonyGeneralInfo = ColonyGeneralInfo()
        self.spore_man: ColonySporeManager = ColonySporeManager(
            self.width,
            self.height,
            init_pop
        )
        self.happiness_man: HappinessManager = HappinessManager(base=15.0)
        self.building_man: ColonyBuildingManager = ColonyBuildingManager()
        self.res_man: ColonyResourceManager = ColonyResourceManager(
            self.spore_man,
            self.happiness_man,
            self.building_man
        )

        # utilities
        self.rng = np.random.RandomState(seed)
        self.printer: InfoManager = InfoManager(silent_mode=(not verbose))

        
    def _check_die_out(self) -> bool:
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
        # add resources gathered by spores

        # random food list, if a spore chooses to take
        food_takes: np.ndarray

        # variables for other calculations
        healths: List[float] = []

        # process spores by tile
        for coor, spores_in_tile in self.step.items():
            # process each spore on this tile
            for spore_inlist_id, spore_id in enumerate(spores_in_tile):
                s: Spore = self.spores[spore_id]
                # spore consumes resource (food)
                if self.storage.res[11] > 0:  # food
                    self.storage.res[11] -= 1
                else:
                    s.health -= self.rng.uniform(1, 20)  # food shortage, hurting health

                # spore ages
                s.age += 1

                healths.append(s.health)
                # spore health check
                if s.health <= 0:
                    self._remove_spore(spore_id)
                    del self.step[coor][spore_inlist_id]
                    if (self.step[coor]) == 0:
                        del self.step[coor]

                # spore takes food

        # calculate happiness
        expansion_ready: bool = self.happiness_man.update(healths)
        if expansion_ready and self.current_pop < self.pop_cap:
            self._create_individual(sex=self.rng.choice(list(sex_mapper.keys())))

    def progress_a_step(self):
        """
        Progress to the next step.

        Returns:
            bool: if the colony dies.
        """
        # calculate the current step, because progression will be based it results of current step
        self.calculate_current_step()

        # save current step
        if self.enable_history:
            self.step_record.append(self.step.copy())

        if not self._check_die_out():
            self.printer.info("Colony failed, spores unable to reproduce.")
            return False

        spore_step: Dict[Tuple[int, int], List[int]] = self.spore_man.progress_spore_step()
        self.step = spore_step
        self.current_iteration += 1

        return True
