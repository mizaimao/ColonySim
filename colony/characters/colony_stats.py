"""Classes managing colony stats."""
from typing import Dict, List, Tuple

from colony.configuration import res_cfg
from colony.characters.spore import Spore, ColonySporeManager
from colony.characters.storage import ColonyStorage, SporeStorage
from colony.characters.buildings import ColonyBuildingManager
from colony.utils.batch_random import BatchUniform, BatchNormal

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

    def __init__(
        self,
        spore_man: ColonySporeManager,
        happiness_man: HappinessManager,
        building_man: ColonyBuildingManager,
        seed: int = 720
    ):

        # setup pointers to Colony instance
        self.spore_man: ColonySporeManager = spore_man
        self.building_man: ColonyBuildingManager = building_man
        self.happiness_man: HappinessManager = happiness_man

        self.storage: ColonyStorage = ColonyStorage(res_cfg.starting_res)

        # setup random number generators for resource income and consumption
        food_gaithring_speed: float = res_cfg.income_speed[11][0]
        food_consumption_per_pop: int = res_cfg.food_consumption_per_pop
        self.food_gaithring_rng: BatchNormal = BatchNormal(
            seed, mean=food_gaithring_speed, std=food_gaithring_speed * res_cfg.income_speed_std_pct[11] 
        )
        self.food_consumption_rng: BatchNormal = BatchNormal(
            seed, mean=food_consumption_per_pop, std=food_consumption_per_pop * res_cfg.income_speed_std_pct[11] 
        )

        # how much man power assigned for each types of resource
        self.res_manpower: Dict[int, int] = {}  # {resource_type: manpower}

    def progress_res_step(self):
        # add food collected by spores to colony storage
        # and calculate food consumption/distribution by spores
        self._calculate_food_from_spores_collection()

        pass

    def _calculate_food_from_spores_collection(self):
        food_consumption_per_pop: float = self.food_consumption_rng.get()

        for sid, spore in self.spore_man.spores.items():
            # spore now put their collected food into colony's storage
            food_gaithered_by_this_spore: float = self.food_gaithring_rng.get()
            self.storage.res[11] += food_gaithered_by_this_spore

            # spore consumes food, and uptate amount in its storage
            # the spore always take food from its own storage first, and then grabs from colony stroage
            additional_food_unit: int = 0  # variable tracks additional food to take in order to fill spores belly
            if spore.storage.res[11] > food_consumption_per_pop:  # spore's own storage minus food amount it consumes
                spore.storage.res[11] -= food_consumption_per_pop
            else:  # spore consumes all food in its own storage, and would need to grab some more from colony storage
                additional_food_unit = food_consumption_per_pop - spore.storage.res[11]
                food_to_grab_from_colony_storage: int = spore.storage.resource_limit + additional_food_unit
            
                # colony storage can cover all food required for this spore
                if self.storage.res[11] > food_to_grab_from_colony_storage:
                    self.storage.res[11] -= food_to_grab_from_colony_storage
                    spore.storage.res[11] = spore.storage.resource_limit
                else:  # colony storage will be emptied, and spore's stroage cannot be filled fully
                    self.storage.res[11] = 0
                    spore.storage.res[11] = max(0, food_to_grab_from_colony_storage - spore.storage.res[11])

    def calculate_all_income(self):
        """Calculate income of each types of resources and update to colony storage."""
        pass

    def calculate_all_comsumption(self):
        """Calculate income of each types of resources and update to colony storage."""
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
