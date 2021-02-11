import numpy as np
import cv2


class PopulationCurve:
    def __init__(self):
        self.initialized = False

    def setup(self, width: int, height: int):
        self.width = width
        self.height = height
        self.plottable_height = int(self.height * 0.90)

        self.prev_high = 1
        self.data = [] # queue

        self.initialized = True

    def update_and_plot(self, point: int):
        """
        Soak a new value and add to queue, also return the
        updated plot.
        """
        # if reaches the max size, remove the first element
        if len(self.data) == (self.width - 1):
            self.data.pop(0)
            
        # append the new element
        self.data.append(point)

        # update high
        self.prev_high = max(self.prev_high, point)

        plot = np.full((self.height, self.width, 3), 240, dtype=np.uint8)
        for ri, value in enumerate(self.data[::-1]): # reversed index
            plot[self.plottable_height - int(value/self.prev_high*self.plottable_height), self.width - ri - 1] = (80, 30, 00)
        
        return plot