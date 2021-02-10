import numpy as np

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
    x, y = coor
    if x_low <= x < x_high and y_low <= y < y_high:
        return True
    return False 

    