"""Classes managing colony stats."""
from typing import Dict, List

from colony.configuration import res_cfg
from colony.characters.spore import Spore
from colony.characters.storage import ColonyStorage, SporeStorage

# backtracking histroy length
MAX_TRACKING: int = 1000

# lager -> slower progress bar of population-expansion-ready flag
POP_PROGRESS_DIVIDER: float = 10.


class HappinessManager:
    """Calculates colony happiness."""
    def __init__(self, base: float):
        self.base: float = base

        self.last_pop: int = 0
        self.next_pop_progress: float = 0.
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
        if pop > self.last_pop:  # indicates colony expanded, therefore empty progress bar
            self.next_pop_progress = 0.
            self.last_pop = pop
        # health

        new_hpy: float = self.base
        self.next_pop_progress = min(
            self.next_pop_progress + new_hpy / POP_PROGRESS_DIVIDER, 100.
        )

        self.history.append(new_hpy)
        if len(self.history) == MAX_TRACKING + 1:
            self.history.pop(0)

        expansion_ready: bool = self.next_pop_progress >= 100.
        return expansion_ready


class ColonyResourceManager:
    """Mananges colony resources, like auto-harvest income and distribution."""
    def __init__(self, spore: Dict[int, Spore], storage: ColonyStorage):

        # setup pointers to Colony instance
        self.spores: Dict[int, Spore] = spore
        self.storage: ColonyStorage = storage

        

        pass