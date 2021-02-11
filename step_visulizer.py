import numpy as np
from colony import Colony
from population_plotter import PopulationCurve
import cv2

# color in BGR 
color_dict = {1: (245, 158, 66), 3: (95, 95, 250)}

def convert_step_to_array(colony: Colony, multiplier: float = 30.0, cycle: int = -1, pop_curve: PopulationCurve = None):
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
    info_pane_height = int(frame_height * 0.2) 
    left_info_pane_width = int(frame_width / 2)
    right_info_pane_width = frame_width - left_info_pane_width

    left_info = np.full((info_pane_height, left_info_pane_width, 3), 220, dtype=np.uint8)
    cv2.putText(left_info, 
        "Colony Size: {}".format(colony.current_pop),  # text
        (20, 50),  # pos
        cv2.FONT_HERSHEY_SIMPLEX, # font
        1.5, # scale
        (100, 100, 100), # front color
        3)  # linetype
    cv2.putText(left_info, 
        "Cycle: {}".format(cycle),  # text
        (20, 100),  # pos
        cv2.FONT_HERSHEY_SIMPLEX, # font
        1.5, # scale
        (100, 100, 100), # front color
        3)  # linetype

    if not pop_curve.initialized:
        pop_curve.setup(width=right_info_pane_width, height=info_pane_height)
    right_plot = pop_curve.update_and_plot(colony.current_pop)

    below_addon = np.concatenate([left_info, right_plot], axis=1)

    return np.concatenate([frame, below_addon], axis=0)