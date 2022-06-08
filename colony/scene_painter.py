"""Painter functions to draw 2D or isometric views of upper panel.
"""
from abc import ABC, abstractmethod
from typing import Callable, Tuple
import cv2
import numpy as np
from configs.map_generator.ref import map_ref


class ColonyView(ABC):
    """Upper viewing panel drawer.
    """
    def __init__(self,
                frame_height: int,
                frame_width: int,
                bitmap,
                multiplier: float):
        self.frame_height: int = frame_height
        self.frame_width: int = frame_width
        self.bitmap = bitmap
        self.multiplier: float = multiplier
        self.static_frame: np.ndarray = None

    @abstractmethod
    def get_static_frame(self):
        pass

    @abstractmethod
    def _paint_background(self):
        """Add background to """
        pass

    @abstractmethod
    def _paint_large_pixel(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Add individual large "pixels" onto scene."""
        pass

class ColonyView2D(ColonyView):
    def __init__(self, frame_height: int, frame_width: int, bitmap, multiplier: float):
        super().__init__(frame_height, frame_width, bitmap, multiplier)

    def get_static_frame(self):
        if not self.static_frame:
            self.static_frame = np.full((self.frame_height, self.frame_width, 3), 255, dtype=np.uint8)
        return self.static_frame


    def _paint_background(self):
        for y in range(len(self.bitmap)):
            for x in range(len(self.bitmap[0])):
                color = map_ref[self.bitmap[y][x]][-1]
                self._paint_large_pixel(self.static_frame, y, x, color)

    def _paint_large_pixel(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Print a big pixel element on the given frame
        """
        x_start = int(x * self.multiplier)
        x_end = int((x+1) * self.multiplier)
        y_start = int(y * self.multiplier)
        y_end = int((y+1) * self.multiplier)

        frame[y_start:y_end, x_start:x_end] = color

class ColonyViewIso(ColonyView):
    pass