import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple, List

from colony.characters.storage import SporeStorage
from colony.progression.step import get_direction, get_next_coor



sex_mapper = {1: "A", 3: "B"}
INITAL_HEALTH: int = 100
INITIAL_POPCAP: int = 40


@dataclass
class Spore:
    sid: int
    sex: int
    age: int
    health: int

    storage: SporeStorage


class ColonySporeManager:
    """Manages all spores in a colony.
    """
    def __init__(self, width: int, height: int, init_pop: int, pop_cap: int = INITIAL_POPCAP, seed: int = 720):
        # size of colony
        self.width: int = width
        self.height: int = height
        # poplulation cap
        self.pop_cap: int = pop_cap

        # incremental spore id
        self.id_counter: int = 0
        # stores all spores
        self.spores: Dict[int, Spore] = {}
        # current locations where there are nay spores
        self.step: Dict[Tuple[int, int], List[int]] = {}
    
        # other settings
        self.allow_init_overlapping: bool = False
        self.rng = np.random.RandomState(seed=seed)

        # initial population
        self.current_pop: int = 0
        # create the inital cohort
        self.create_init_population(init_pop)
    

    def update_population(self):
        return len(self.spores)

    def __len__(self):
        return self.current_pop


    def create_init_population(self, init_pop: int):
        color_0: int = 1
        color_1: int = 3

        color_0_count: int = int(init_pop / 2)
        color_1_count: int = init_pop - color_0_count

        for _ in range(color_0_count):
            self.add_a_spore(sex=color_0)
        for _ in range(color_1_count):
            self.add_a_spore(sex=color_1)


    def add_a_spore(self, sex: int, coor: Tuple[int, int] = None):
        """
        Create a new spore with given sex (required) and coor (optional)
        """
        if coor is None:
            # get a fresh pair of coor
            x: int = self.rng.randint(low=0, high=self.width)
            y: int = self.rng.randint(low=0, high=self.height)

            # roll the coor of spore
            if not self.allow_init_overlapping:
                while (x, y) in self.step:
                    x = self.rng.randint(low=0, high=self.width)
                    y = self.rng.randint(low=0, high=self.height)
        else:
            x, y = coor
            if coor in self.step and (not self.allow_init_overlapping):
                raise ValueError(f"Given coor is already occupied {coor}")

        # create a spore and add it to colony tracking dict
        s: Spore = Spore(
            sid=self.id_counter,
            sex=sex,
            age=0,
            health=INITAL_HEALTH,
            storage=SporeStorage(),
        )
        # add to spore dict
        self.spores[s.sid] = s
        # add spore to step
        coor: Tuple[int, int] = (x, y)
        if coor not in self.step:
            self.step[coor] = []
        self.step[coor].append(s.sid)
        # update counters
        self.id_counter += 1
        self.current_pop += 1

    def remove_a_spore(self, spore_id: int):
        """Remove a spore from colony (e.g. death)."""
        del self.spores[spore_id]
        self.current_pop -= 1

    def progress_spore_step(self):
        # processed step placeholder
        new_step = {}
        # generate next moves of spores in a batch
        next_directions = get_direction(size=self.current_pop)

        spore_counter: int = 0
        # process spores by tile
        for coor, spores_in_tile in self.step.items():
            # process each spore on this tile
            for spore_id in spores_in_tile:
                # spore movement
                new_coor = get_next_coor(
                    next_directions[spore_counter],
                    coor,
                    self.width,
                    self.height,
                    new_step,
                )
                # change tiles according to their movements
                if new_coor not in new_step:
                    new_step[new_coor] = []
                new_step[new_coor].append(spore_id)
                spore_counter += 1

        self.step = new_step
        return self.step
