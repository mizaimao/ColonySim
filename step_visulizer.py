import numpy as np
from colony import Colony
import cv2

color_dict = {1: (0, 0, 255), 3: (255, 0, 0)}

def convert_step_to_array(colony: Colony, multiplier: float = 30.0):
    """
    Visualize a single step in colony.
    """
    # create an RGB array
    frame_height = int((colony.height) * multiplier) 
    frame_width = int((colony.width) * multiplier)
    frame = np.full((frame_height, frame_width, 3), 255, dtype=np.uint8)
    #frame[:,:,:] = 255

    spore_side = int(multiplier)

    for (x, y), spores in colony.step.items():
        #print(x, y)
        x_start = int(x * multiplier)
        x_end = int((x+1) * multiplier)
        y_start = int(y * multiplier)
        y_end = int((y+1) * multiplier)
        #print(x_start, x_end, y_start, y_end)

        top_spore = colony.spores[spores[0]]

        frame[y_start:y_end, x_start:x_end] = color_dict[top_spore.sex]
        #frame[x_start:x_end, y_start:y_endd] = (0, 0, 255)

    # displaying info 
    below_addon = np.full((int(frame_height * 0.2), frame_width, 3), 220, dtype=np.uint8)
    
    cv2.putText(below_addon, 
        "Colony Size: {}".format(len(colony.spores)),  # text
        (20, 50),  # pos
        cv2.FONT_HERSHEY_SIMPLEX, # font
        2, # scale
        (0, 0, 0), # front color
        2)  # linetype

    return np.concatenate([frame, below_addon], axis=0)