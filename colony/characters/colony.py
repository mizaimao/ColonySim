import numpy as np
from dataclasses import dataclass, field
from typing import Dict, Tuple, List

from colony.characters.spore import Spore
from colony.step_progression import *
from colony.configuration import spore_cfg
from colony.utils.info_manager import InfoManager


sex_mapper = {1: "A", 2: "a", 3: "B", 4: "b"}


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
        self.width = width
        self.height = height
        self.viewer_width = viewer_width
        self.viewer_height = viewer_height
        self.allow_init_overlapping = True
        self.enable_history = False
        self.step = {}
        self.id_counter = 0
        self.current_pop = 0
        self.spores = {} # stores all shown spores
        self.info = ColonyGeneralInfo()
        self.printer = InfoManager(silent_mode=(not verbose))

        self.step_record = [] # a record of each step

        self._initial_locations = [] # will be emptied after init
        for i in range(init_pop):
            
            if i % 2 == 0:
                sex = 1
            else:
                sex = 3
            if not sex in self.info.gender_counts:
                self.info.gender_counts[sex] = 0
            self.info.gender_counts[sex] += 1

            self._create_individual(sex=sex, step_dict=self.step)

        
    def _create_individual(self, sex: int, coor: tuple = None, step_dict = None):
        """
        Create a new spore with given sex (required) and coor (optional)
        """
        if coor is None:
            # get a fresh pair of coor
            x = np.random.randint(low=0, high=self.width)
            y = np.random.randint(low=0, high=self.height)
            
            # roll the coor of spore
            if self.allow_init_overlapping == False:
                while (x, y) in step_dict:
                    x = np.random.randint(low=0, high=self.width)
                    y = np.random.randint(low=0, high=self.height)
        else: 
            x, y = coor

        # create a spore and add it to colony tracker dict
        s = Spore(sid=self.id_counter, sex=sex)
        # add spore pointer
        self.spores[s.sid] = s

        # add spore to step
        try:
            step_dict[(x, y)].append(s.sid)
        except KeyError:
            step_dict[(x, y)] = [s.sid]
        self.info.gender_counts[sex] += 1

        self.id_counter += 1
        self.current_pop += 1


    def _check_die_out(self):
        """Checks if a colony reaches certerion that do not permit progression.
        For example, a certain gender dies out.

        Returns
            bool: true if passes the test and the colony survives.
        """
        # check distinguishing by gender
        for gender_counter in self.info.gender_counts.values():
            if gender_counter == 0:
                return False

        return True


    def progress_a_step(self):
        """
        Generate the next step.

        Args: 
            step {dict} -- record of current step
            pop {int} -- population of current step

        Returns:
            bool: if the colony dies
        """
        # save current step
        if self.enable_history:
            self.step_record.append(self.step.copy())

        if not self._check_die_out():
            self.printer.info("Colony failed, spores unable to reproduce.")
            return False

        # processed step placeholder
        new_step = {} 

        # generate spres' next move in a batch
        next_directions = get_direction(size=self.current_pop)
        
        spore_counter = 0
        events = {}
        
        # process spores by tile
        for coor, spores_in_tile in self.step.items():
            encounter = False
            crowd_size = len(spores_in_tile)

            # too crowded, triggering extinct on tile
            if crowd_size > spore_cfg.crowd_threshold: 
                self.printer.info(f"A crowd of {crowd_size} dead caused by famine,")
                for spore_id in spores_in_tile:
                    del self.spores[spore_id]
                        
                self.current_pop -= crowd_size
                spore_counter += crowd_size
                continue

            # more than one spre on tile, triggering event
            if crowd_size > 1:
                encounter = True 

                # select two spores
                chosen_ids = np.random.choice(spores_in_tile, size = 2, replace=False)
                # get result of their encounter
                event_results = event_handler(self.spores[chosen_ids[0]], self.spores[chosen_ids[1]])
                survival_dict = {chosen_ids[0]: event_results[0][0],
                                chosen_ids[1]: event_results[0][1]}
                # add event record so that it can be processed later
                # cannot be processed now since it changes dict size
                events[coor] = (survival_dict, event_results[1])

            # process each spore on this tile
            for spore_id in spores_in_tile:
                if encounter:
                    try:
                        survived = survival_dict[spore_id]
                    except KeyError: # if they are not in survival event, then safe
                        survived = True
                    
                    if not survived: # delete this spore
                        spore_pointer = self.spores[spore_id]
                        self.info.gender_counts[spore_pointer.sex] -= 1  # substract its gender counter
                        del self.spores[spore_id]
                        self.printer.info("A spore dead in fighting.")
                        self.current_pop -= 1
                        spore_counter += 1
                        continue
                
                # safe spores proceeds to this step, so they will mobilize 
                next_direction = next_directions[spore_counter]
                new_coor = get_next_coor(next_direction, coor, self.width, self.height)

                # change tiles according to their movements
                try:
                    new_step[new_coor].append(spore_id)
                except KeyError:
                    new_step[new_coor] = [spore_id]

                spore_counter += 1

        for coor, (survival_dict, new_born) in events.items():
            for new_born in range(event_results[1]):
                sex = 1 if np.random.random() <= 0.5 else 3
                neary_by_coor = get_next_coor(get_direction(), coor, self.width, self.height)

                self._create_individual(sex=sex,
                                        coor=neary_by_coor,
                                        step_dict=new_step)
                self.printer.info(f"A new baby was born, new pop: {self.current_pop}.")

        self.step = new_step

        return True