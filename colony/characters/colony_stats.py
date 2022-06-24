"""Classes managing colony stats."""
from typing import Dict, List
from colony.characters.spore import Spore

# backtracking histroy length
MAX_TRACKING: int = 1000

class HappinessManager:
    """Calculates colony happiness."""
    def __init__(self, base: float):
        self.base: float = base

        self.history: List[float] = [base]  # queue

    def update(self, spores: Dict[int, Spore]):
        # negative impacts
        # population
        pop: int = len(spores)
        # health

        new_hpy: float = self.base
        self.history.append(new_hpy)
        if len(self.history) == MAX_TRACKING + 1:
            self.history.pop(0)
