"""Classes managing colony stats."""
from typing import Dict, List, Tuple

from colony.configuration import res_cfg
from colony.characters.spore import Spore, ColonySporeManager
from colony.characters.storage import ColonyStorage, SporeStorage
from colony.characters.buildings import ColonyBuildingManager

# backtracking histroy length
MAX_TRACKING: int = 1000

# lager -> slower progress bar of population-expansion-ready flag
POP_PROGRESS_DIVIDER: float = 10.0


class HappinessManager:
    """Calculates colony happiness."""

    def __init__(self, base: float):
        self.base: float = base

        self.last_pop: int = 0
        self.next_pop_progress: float = 0.0
        self.history: List[float] = [base]  # queue

    def update(self, healths: List[float]) -> bool:
        """Update current happiness based on colony stats.
        Returns whether the colony is ready to expand one new population.
        """
        # negative impacts
        # population
        pop: int = len(healths)

        if self.last_pop == 0:
            self.last_pop = pop
        if (
            pop > self.last_pop
        ):  # indicates colony expanded, therefore empty progress bar
            self.next_pop_progress = 0.0
            self.last_pop = pop
        # health

        new_hpy: float = self.base
        self.next_pop_progress = min(
            self.next_pop_progress + new_hpy / POP_PROGRESS_DIVIDER, 100.0
        )

        self.history.append(new_hpy)
        if len(self.history) == MAX_TRACKING + 1:
            self.history.pop(0)

        expansion_ready: bool = self.next_pop_progress >= 100.0
        return expansion_ready


class ColonyResourceManager:
    """Mananges colony resources, like auto-harvest income and distribution."""

    def __init__(self, spore_man: ColonySporeManager, happiness_man: HappinessManager, buildings: ColonyBuildingManager):

        # setup pointers to Colony instance
        self.spore_man: ColonySporeManager = spore_man
        self.buildings: ColonyBuildingManager = buildings
        self.happiness_man: HappinessManager = happiness_man

        self.storage: ColonyStorage = ColonyStorage(res_cfg.starting_res)

        # how much man power assigned for each types of resource
        self.res_manpower: Dict[int, int] = {}  # {resource_type: manpower}

    def calculate_all_income(self):
        """Calculate income of each types of resources and update to colony storage.
        """
        pass
    

    def calculate_all_comsumption(self):
        """Calculate income of each types of resources and update to colony storage.
        """
        pass

    def _calculate_income(self, res: int):
        """Calculate specific type of resource of income.

        Args
            res: resource type.
        """
        pass


    def _calculate_comsumption(self, res: int):
        """Calculate specific type of resource of consumtion.

        Args
            res: resource type.
        """
        pass
