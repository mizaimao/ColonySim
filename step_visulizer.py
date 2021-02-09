import numpy as np
from colony import Colony

def convert_step_to_array(colony: Colony, multiplier: float = 30.0):
    """
    Visualize a single step in colony.
    """
    # create an RGB array
    frame = np.zeros((int((colony.height) * multiplier), int((colony.width) * multiplier), 3), dtype=np.uint8)
    frame[:,:,:] = 255

    spore_side = int(multiplier)

    for (x, y), spores in colony.step.items():
        print(x, y)
        x_start = int(x * multiplier)
        x_end = int((x+1) * multiplier)
        y_start = int(y * multiplier)
        y_end = int((y+1) * multiplier)
        print(x_start, x_end, y_start, y_end)

        frame[y_start:y_end, x_start:x_end] = (0, 0, 255)
        #frame[x_start:x_end, y_start:y_endd] = (0, 0, 255)

    return frame