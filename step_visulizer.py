import numpy as np
from colony import Colony
from population_plotter import PopulationCurve
import cv2

# color in BGR 
color_dict = {1: (245, 158, 66), 3: (95, 95, 250)}


class StepVisulizer:
    """
    Visualize a single step in colony.
    """
    def __init__(self, colony: Colony, multiplier: float = 30.0, pop_curve: PopulationCurve = None):
        # fixed values
        self.frame_height = int((colony.height) * multiplier) 
        self.frame_width = int((colony.width) * multiplier)
        # displaying info 
        self.info_pane_height = int(self.frame_height * 0.2) 
        self.left_info_pane_width = int(self.frame_width / 2)
        self.right_info_pane_width = self.frame_width - self.left_info_pane_width

        # pointers
        self.multiplier = multiplier
        self.colony = colony

        self.pop_curve = PopulationCurve()
        self.pop_curve.setup(width=self.right_info_pane_width, height=self.info_pane_height)

    def plot_step(self, cycle: int = -1):
        frame = np.full((self.frame_height, self.frame_width, 3), 255, dtype=np.uint8)

        # upper pane
        for (x, y), spores in self.colony.step.items():
            #print(x, y)
            x_start = int(x * self.multiplier)
            x_end = int((x+1) * self.multiplier)
            y_start = int(y * self.multiplier)
            y_end = int((y+1) * self.multiplier)
            #print(x_start, x_end, y_start, y_end)

            top_spore = self.colony.spores[spores[0]]

            frame[y_start:y_end, x_start:x_end] = color_dict[top_spore.sex]
       
        # lower panes
        left_info = np.full((self.info_pane_height, self.left_info_pane_width, 3), 220, dtype=np.uint8)
        cv2.putText(left_info, 
            "Colony Size: {}".format(self.colony.current_pop),  # text
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
            
        right_plot = self.pop_curve.update_and_plot(self.colony.current_pop)

        below_addon = np.concatenate([left_info, right_plot], axis=1)

        return np.concatenate([frame, below_addon], axis=0)