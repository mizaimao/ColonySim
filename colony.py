import json
import numpy as np
from spore import Spore
from step_progression import spore_step, validate_coor

sex_mapper = {1: "A", 2: "a", 3: "b", 4: "B"}

class Colony:
    """
    A colony with width and height, inside multiple individuals will be 
    spawned and may encounter each other tirggering potential destruction 
    or multiplication.
    """
    def __init__(self, width: int = 32, height: int = 16, 
                init_pop: int = 10, seed: int = 0):
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
        self.allow_init_overlapping = True
        self.enable_history = False
        #self.map = np.zeros((width, height), dtype=np.uint8)
        self.step = {}
        self.id_counter = 0
        self.current_pop = 0
        self.spores = {} # stores all shown spores

        self.step_record = [] # a record of each step

        self._initial_locations = [] # will be emptied after init
        for i in range(init_pop):
            
            if i % 2 == 0:
                sex = 1
            else: 
                sex = 4

            self._create_individual(sex=sex)

        
    def _create_individual(self, sex: int):
        # get a fresh pair of coor
        x = np.random.randint(low=0, high=self.width)
        y = np.random.randint(low=0, high=self.height)
        
        # roll the coor of spore
        if self.allow_init_overlapping == False:
            while (x, y) in self.step:
                x = np.random.randint(low=0, high=self.width)
                y = np.random.randint(low=0, high=self.height)
        
        # create a spore and add it 
        s = Spore(sid=self.id_counter, sex=sex)
        # add spore pointer
        self.spores[s.sid] = s

        # add spore to step
        try:
            self.step[(x, y)].append(s.sid)
        except KeyError:
            self.step[(x, y)] = [s.sid]

        self.id_counter += 1
        self.current_pop += 1


    def progress_a_step(self):
        """
        Generate the next step.

        Args: 
            step {dict} -- record of current step
            pop {int} -- population of current step

        Returns:
            dict -- next step 
        """
        # save current step
        if self.enable_historyd:
            self.step_record.append(self.step.copy())

        new_step = {}
        
        next_directions = np.random.randint(low=0, high=9, size=self.current_pop)
        
        spore_counter = 0
        for coor, spores_in_tile in self.step.items():
            """
            event_trigger = False
            if len(spores_in_tile) > 1:
                event_trigger = True 

                chosen_ids = np.random.choice(spores_in_tile, size = 2, replace=False)
            """
            for spore_id in spores_in_tile:
                next_direction = next_directions[spore_counter]
                while True: # do-while loop in python
                    new_coor = spore_step(direction = next_direction, current_coor = coor)
                    if validate_coor(0, self.width, 0, self.height, new_coor):
                        break
                    next_direction = np.random.randint(low=0, high=9)

                try:
                    new_step[new_coor].append(spore_id)
                except KeyError:
                    new_step[new_coor] = [spore_id]

                spore_counter += 1

        self.step = new_step


    

