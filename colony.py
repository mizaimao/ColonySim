import numpy as np
from spore import Spore

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
        self.spores = []

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
        self.spores.append(s)

        # add spore to step
        try:
            self.step[(x, y)].append(s.sid)
        except KeyError:
            self.step[(x, y)] = [s.sid]

        self.id_counter += 1

    #def _start(self):
