import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

from colony.characters.colony_stats import HappinessManager
from colony.characters.spore import Spore, FOOD_SPEED, RES21_SPEED, RES22_SPEED, RES23_SPEED
from colony.characters.storage import ColonyStorage
from colony.progression.step import *
from colony.configuration import spore_cfg, res_cfg, ResSetup
from colony.utils.info_manager import InfoManager


sex_mapper = {1: "A", 3: "B"}
INITAL_HEALTH: int = 100

@dataclass
class ColonyGeneralInfo:
    gender_counts: Dict[int, int] = field(default_factory=dict)



class Colony:
    """
    A colony with width and height, inside multiple individuals will be 
    spawned and may encounter each other tirggering potential destruction 
    or multiplication.
    """
    def __init__(self,
                width: int = 32,
                height: int = 16,
                viewer_width: int = 1440,
                viewer_height: int = 900,
                init_pop: int = 10,
                res_cfg: ResSetup = res_cfg,
                seed: int = 0,
                verbose: bool = True):
        """
        Args:
            init_pop {int}: inital population. Now only two types which 
                are males and females, divided evenly.
            allow_init_overlapping {bool}: two individuals can start at the
                same location.
            enable_history {bool}: record each step colony takes.
            
        """
        # settings
        self.width: int = width
        self.height: int = height
        self.viewer_width: int = viewer_width
        self.viewer_height: int = viewer_height
        self.allow_init_overlapping: bool = False
        self.enable_history: bool = False

        # variables
        self.step: Dict[Tuple[int, int], List[int]] = {}
        self.id_counter: int = 0
        self.current_pop: int = 0
        self.current_iteration: int = 0
        self.step_record: list = [] # a record of each step  # typing???

        # progress variables
        self.tech_stage: int = 0
        self.happiness: HappinessManager = HappinessManager(base=15.)
        self.pop_cap: int = 40

        # pointers
        self.spores: Dict[int, Spore] = {} # stores all shown spores
        self.info: ColonyGeneralInfo = ColonyGeneralInfo()
        self.printer: InfoManager = InfoManager(silent_mode=(not verbose))
        self.storage: ColonyStorage = ColonyStorage(res=res_cfg.starting_res)
        self.rng = np.random.RandomState(seed)

        # create population
        self._create_init_population(init_pop=init_pop)

    def _create_init_population(self, init_pop: int):
        color_0: int = 1
        color_1: int = 3

        color_0_count: int = int(init_pop / 2)
        color_1_count: int = init_pop - color_0_count

        self.info.gender_counts[color_0] = color_0_count
        self.info.gender_counts[color_1] = color_1_count

        for _ in range(color_0_count):
            self._create_individual(sex=color_0)
        for _ in range(color_1_count):
            self._create_individual(sex=color_1)

    def _create_individual(self, sex: int, coor: tuple = None):
        """
        Create a new spore with given sex (required) and coor (optional)
        """
        if coor is None:
            # get a fresh pair of coor
            x: int = np.random.randint(low=0, high=self.width)
            y: int = np.random.randint(low=0, high=self.height)
            
            # roll the coor of spore
            if not self.allow_init_overlapping:
                while (x, y) in self.step:
                    x = np.random.randint(low=0, high=self.width)
                    y = np.random.randint(low=0, high=self.height)
        else: 
            x, y = coor

        # create a spore and add it to colony tracker dict
        s: Spore = Spore(
            sid=self.id_counter,
            sex=sex,
            age=0,
            health=INITAL_HEALTH)
        # add spore pointer
        self.spores[s.sid] = s

        # add spore to step
        try:
            self.step[(x, y)].append(s.sid)
        except KeyError:
            self.step[(x, y)] = [s.sid]
        self.info.gender_counts[sex] += 1

        self.id_counter += 1
        self.current_pop += 1

    def _remove_spore(self, spore_id: int):
        """Remove a spore from colony (e.g. death).
        """
        self.info.gender_counts[self.spores[spore_id].sex] -= 1
        del self.spores[spore_id]
        self.current_pop -= 1

    def _check_die_out(self) -> bool:
        """Checks if a colony reaches certerion that do not permit progression.
        For example, if there are less than two individuals alive, then the colony dies out.

        Returns
            bool: true if passes the test and the colony survives.
        """
        # check distinguishing by numbers
        return len(self.spores) >= 2

    def calculate_current_step(self):
        """Calculate resource input and output of this step. Spores dead will also be removed. 
        Should be called before progressing to the next step.
        Differences are this function computes the current step, while "progress_a_step" projects
        the next iteration.
        """
        # add resources gathered by spores
        res: Dict[int, int] = self.storage.res
        res[11] += len(self.spores) * FOOD_SPEED[self.tech_stage]  # food
        res[21] += len(self.spores) * RES21_SPEED[self.tech_stage]
        res[22] += len(self.spores) * RES22_SPEED[self.tech_stage]
        res[23] += len(self.spores) * RES23_SPEED[self.tech_stage]

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

        # calculate happiness
        expansion_ready: bool = self.happiness.update(healths)
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
                    new_step)

                # change tiles according to their movements
                if new_coor not in new_step:
                    new_step[new_coor] = []
                new_step[new_coor].append(spore_id)
                spore_counter += 1

        # for coor, (survival_dict, new_born) in events.items():
        #     for new_born in range(event_results[1]):
        #         sex = 1 if np.random.random() <= 0.5 else 3
        #         neary_by_coor = get_next_coor(get_direction(), coor, self.width, self.height)

        #         self._create_individual(sex=sex,
        #                                 coor=neary_by_coor,
        #                                 step_dict=new_step)
        #         self.printer.info(f"A new baby was born, new pop: {self.current_pop}.")

        self.step = new_step


        self.current_iteration += 1

        return True