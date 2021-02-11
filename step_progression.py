import numpy as np
from spore import Spore

from configuration import cfg

def spore_step(direction: int, current_coor: tuple):
    """
    Calculate a spore's next step, and result may not be valid.
    """
    x, y = current_coor
    if direction == 0:
        return (x, y)
    elif direction == 1:
        return (x, y + 1)
    elif direction == 2:
        return (x + 1, y + 1)
    elif direction == 3:
        return (x + 1, y)
    elif direction == 4:
        return (x + 1, y - 1)
    elif direction == 5:
        return (x, y - 1)
    elif direction == 6:    
        return (x - 1, y - 1)
    elif direction == 7:
        return (x - 1, y)
    elif direction == 8:
        return (x - 1, y + 1)
    else:
        raise NotImplementedError("Unknown direction", direction)


def validate_coor(x_low: int, x_high: int, y_low: int, y_high: int, coor: tuple):
    """
    To verify if the generated coor are inside map
    """
    x, y = coor
    if x_low <= x < x_high and y_low <= y < y_high:
        return True
    return False 

    
def determine_event(sex_a: int, sex_b: int):
    """
    Determine event based on sex of two spores.

    Returns:
        int -- event code
    """
    # sex_mapper = {1: "A", 2: "a", 3: "B", 4: "b"}
    # event_mapper = {1: "fight", 2: "proliferate", 0: "nothing"}
    if sex_a == 1:
        if sex_b == 3:
            return 2
        if sex_b == 1:
            return 1

    if sex_b == 1:
        if sex_a == 3:
            return 2
    
    return 0


def event_handler(a: Spore, b: Spore):
    """
    Generate event result of two spores.

    Args:
        a, b {Spore} -- two interactive spores 

    Returns:
        [bool, bool] -- if the two spores survive
        int -- number of newborns
    """
    event_code = determine_event(a.sex, b.sex)
    if event_code == 0:
        return [True, True], 0

    elif event_code == 1: # fight
        fatality = cfg.duel_fatality
        probs = np.random.random(2)
        a_survives = True
        b_survices = True 
        if probs[0] <= fatality: # fatal fight
            a_survives = False
        if probs[1] < fatality: # a dies
            b_survices = False 
        return [a_survives, b_survices], 0
        
    elif event_code == 2: # proliforate 
        probs = np.random.random()
        new_born = 0
        if probs <= cfg.one_night_chance:
            new_born += 1
        return [True, True], new_born

    else:
        raise NotImplementedError()


def get_direction(size: int = 1):
    """
    Get a random number representing eight directions (1-8) or stay (0)
    """
    return np.random.randint(low=0, high=9, size=size)

def get_next_coor(next_direction: int, current_coor: tuple, width: int, height: int):
    """
    Generate the coor of the next step. Only returns valid coor
    """
    while True: # do-while loop in python
        new_coor = spore_step(direction = next_direction, current_coor = current_coor)
        if validate_coor(0, width, 0, height, new_coor):
            break
        next_direction = get_direction(size=1)
    return new_coor

