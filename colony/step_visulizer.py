import numpy as np
from colony import Colony
from population_plotter import PopulationCurve
import cv2

# color in BGR 
color_dict = {1: (245, 158, 66), 3: (95, 95, 250)}


class StepVisulizer:
    """
    Visualize a single step in colony
    """
    def __init__(self, colony: Colony, multiplier: float = 30.0, pop_curve: PopulationCurve = None):
        """
        Args:
            colony {Colony} -- pointer to a colony object saved in memory
            multiplier {float} -- scaling factor of visulization
            pop_curve {PopulationCurve} -- pointer to a curve plotting object in memory
        """
        # fixed values
        self.frame_height = int((colony.height) * multiplier) 
        self.frame_width = int((colony.width) * multiplier)
        self.font_scalar = 0.05 * multiplier
        self.font_space = int(5 / 3 * multiplier)
        self.font_above = int(5 / 3 * multiplier)
        self.font_front = int(2 / 3 * multiplier)
        self.multiplier = multiplier
        # displaying info 
        self.info_pane_height = int(self.frame_height * 0.2) 
        self.left_info_pane_width = int(self.frame_width / 2)
        self.right_info_pane_width = self.frame_width - self.left_info_pane_width
        # pointers to objects in memory
        self.colony = colony
        self.pop_curve = PopulationCurve()
        self.pop_curve.setup(width=self.right_info_pane_width, height=self.info_pane_height)

    def plot_step(self, cycle: int = -1):
        """
        Plot a step. Info is accessed by the pointer to colony object. 
        The plot is made of upper and lower parts:
            upper part contains enlarged representation of current tiles
            lower part contains two panes
                left pane showing current population and cycle number
                right pane showing population curve
                
        Args:
            cycle {int} -- cycle number that will be displayed on info pane
        """
        frame = np.full((self.frame_height, self.frame_width, 3), 255, dtype=np.uint8)
        # upper pane
        for (x, y), spores in self.colony.step.items():
            x_start = int(x * self.multiplier)
            x_end = int((x+1) * self.multiplier)
            y_start = int(y * self.multiplier)
            y_end = int((y+1) * self.multiplier)
            # show only the first spore 
            top_spore = self.colony.spores[spores[0]]
            # dye this block
            frame[y_start:y_end, x_start:x_end] = color_dict[top_spore.sex]
       
        # lower panes
        # left info pane
        left_info = np.full((self.info_pane_height, self.left_info_pane_width, 3), 220, dtype=np.uint8)
        cv2.putText(left_info, "Colony Size: {}".format(self.colony.current_pop),  # text
            (self.font_front, self.font_above), cv2.FONT_HERSHEY_SIMPLEX, self.font_scalar, # font and scale
            (100, 100, 100), 3)  # linetype
        cv2.putText(left_info, "Cycle: {}".format(cycle), (self.font_front, self.font_above + self.font_space),  # pos
            cv2.FONT_HERSHEY_SIMPLEX, self.font_scalar, 
            (100, 100, 100), 3)  

        # right plot pane, making the curve plot
        right_plot = self.pop_curve.update_and_plot(self.colony.current_pop)
        
        # put two panes together
        below_addon = np.concatenate([left_info, right_plot], axis=1)
        return np.concatenate([frame, below_addon], axis=0)
