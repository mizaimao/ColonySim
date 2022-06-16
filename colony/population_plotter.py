import numpy as np
from typing import Tuple, List, Union

import cv2

POP_PANE_COLOR: Union[int, Tuple[int, ...]] = 220
POP_CURVE_COLOR: Tuple[int, ...] = (80, 30, 00)

class PopulationCurve:
    """
    Plot a curve (more precisely, a series of discreted dots)
    """
    def __init__(self, width: int, height: int):
        """
        Now initialize formally the object
        """
        self.width = width
        self.height = height
        self.plottable_height = int(self.height * 0.90)
        print(self.height, self.plottable_height)

        self.prev_high = 1
        self.data = [] # queue

    def update_and_plot(self, point: int):
        """
        Intake a new value and add to queue, then make a plot and 
        and return it
        """
        # if reaches the max size, remove the first element
        if len(self.data) == (self.width - 1):
            self.data.pop(0)
            
        # append the new element
        self.data.append(point)

        # update high
        self.prev_high = max(self.prev_high, point)

        # iterate through the heights in reversed order and plot dots
        plot = np.full((self.height, self.width, 3), POP_PANE_COLOR, dtype=np.uint8)
        for ri, value in enumerate(self.data[::-1]): # reversed index
            plot[self.plottable_height - int(value/self.prev_high*self.plottable_height), self.width - ri - 1] = POP_CURVE_COLOR
        
        return plot
