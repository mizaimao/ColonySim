"""Painter functions to draw 2D or isometric views of upper panel.
"""
from abc import ABC, abstractmethod
from typing import Callable, Tuple
import cv2
import numpy as np
from math import sqrt
from configs.map_generator.ref import map_ref

ISO_UPPER: float = 0.1  # ratio to frame height
ISO_TILE_HEIGHT: float = 0.1  # raito to mega pixel size

ISO_TILE_WIDTH_SCALAR: float = sqrt(3)
ISO_TILE_HEIGHT_SCALAR: float = 1.0
ISO_TILE_LINE_COLOR: Tuple[float, ...] = (100, 100, 100)

STAGE_BACKGROUND = 150  # color for stage level background

class ColonyView(ABC):
    """Upper viewing panel drawer.
    """
    def __init__(self,
                width: int,
                height: int,
                frame_width: int,
                frame_height: int,
                bitmap):
        self.width: int = width
        self.height: int = height
        self.frame_height: int = frame_height
        self.frame_width: int = frame_width
        self.bitmap = bitmap
        self.multiplier: float = None
        self.static_frame: np.ndarray = None

    @abstractmethod
    def get_static_frame(self):
        """Paint the starge background, and then add empty playground.
        Stage background is the back-most layer, and playground is the space where each dot moves around.
        """
        pass

    @abstractmethod
    def _paint_playground(self):
        """Paint playground."""
        pass

    @abstractmethod
    def _paint_large_pixel(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Add individual large "pixels" onto scene/playground."""
        pass

class ColonyView2D(ColonyView):
    def __init__(self, width: int, height: int, frame_width: int, frame_height: int, bitmap):
        super().__init__(width, height, frame_width, frame_height, bitmap)

        # if colony shape is different from viewer shape, some spaces must be padded.
        self.left_blank: int = 0  # blank space on leftside
        self.top_blank: int = 0  # blank space on top
        
        # because we now separated viwer shape and colony shape, there should be a value we use to map colony dots to
        # viewer.
        self._figure_out_multiplier()

    def _figure_out_multiplier(self):
        """To figure out a scalar that we can use to map individual dots to playground by giving them a size.
        """
        multiplier_x: float = self.frame_width / self.width
        multiplier_y: float = self.frame_height / self.height
        self.multiplier = min(multiplier_x, multiplier_y)

        # in 2D viewer, either X or Y is fully extended, so we only need only blak
        blank: int = int(abs(self.frame_width - self.frame_height) / 2)

        if multiplier_x > multiplier_y:
            self.left_blank = blank
        else:
            self.top_blank = blank

    def get_static_frame(self):
        """Paint the background.
        """
        if not self.static_frame:
            self.static_frame = np.full((self.frame_height, self.frame_width, 3), STAGE_BACKGROUND, dtype=np.uint8)
        return self.static_frame

    def _paint_playground(self):
        """Paint playground.
        """
        for y in range(len(self.bitmap)):
            for x in range(len(self.bitmap[0])):
                color = map_ref[self.bitmap[y][x]][-1]
                self._paint_large_pixel(self.static_frame, y, x, color)

    def _paint_large_pixel(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Paint a big pixel element on the given frame.
        """
        x_start = int(x * self.multiplier) + self.left_blank
        x_end = int((x+1) * self.multiplier) + self.left_blank
        y_start = int(y * self.multiplier) + self.top_blank
        y_end = int((y+1) * self.multiplier) + self.top_blank

        frame[y_start:y_end, x_start:x_end] = color


class ColonyViewIso(ColonyView):
    def __init__(self, width: int, height: int, frame_width: int, frame_height: int, bitmap):
        assert width == height, f"Isometric view supports only square playground, got {(width, height)}"
        super().__init__(width, height, frame_width, frame_height, bitmap)

        # if colony shape is different from viewer shape, some spaces must be padded.
        self.left_blank: int = 0  # blank space on leftside
        self.top_blank: int = 0  # blank space on top
        self.tile_height: float = 0  # fake-3D gets a Z metric

        # figure out multiplier when projecting into isometric spaces
        self._figure_out_multiplier()

    def _figure_out_multiplier(self):
        # this "traditional" multiplier set is used to scale UI stuffs
        multiplier_x: float = self.frame_width / self.width
        multiplier_y: float = self.frame_height / self.height
        self.multiplier = min(multiplier_x, multiplier_y)

        # this isotromic multiplier set is used to draw tiles
        multiplier_x_iso: float = self.frame_width / (self.width * ISO_TILE_WIDTH_SCALAR)
        multiplier_y_iso: float = self.frame_height / (self.height * ISO_TILE_HEIGHT_SCALAR)
        self.multiplier_iso = min(multiplier_x_iso, multiplier_y_iso)
    
        self.tile_width: float = self.multiplier_iso * ISO_TILE_WIDTH_SCALAR
        self.tile_height: float = self.multiplier_iso * ISO_TILE_HEIGHT_SCALAR

        # height offset is needed to "shift" pixles to right by half of playground width
        # different maths requires x-shifting, but it's not the case here
        self.width_offset: float = 0
        self.height_offset: float = self.tile_height * self.height / 2

    def _get_iso_coor(self, x: float, y: float):
        """Convert bitmap coordinates to isometric coordinates."""
        return (
            int((x * self.tile_width / 2) + (y * self.tile_width / 2) + self.width_offset),
            int((y * self.tile_height / 2) - (x * self.tile_height / 2) + self.height_offset)
        )


    def _paint_isometric_static_frame(self):
        frame = np.full((self.frame_height, self.frame_width, 3), STAGE_BACKGROUND, dtype=np.uint8)

        # add x lines to frame
        # from (0, Y0) to (x, Y0) until (0, Yy) to (x, Yy)
        for y in range(self.height + 1):
            start_point = self._get_iso_coor(0, y)
            end_point = self._get_iso_coor(self.width, y)
            cv2.line(frame, start_point, end_point, color=ISO_TILE_LINE_COLOR, thickness=4)
        # add y lines to frame
        # from (X0, 0) to (X0, y) until (Xx, 0) to (Xx, y)
        for x in range(self.width + 1):
            start_point = self._get_iso_coor(x, 0)
            end_point = self._get_iso_coor(x, self.height)
            cv2.line(frame, start_point, end_point, color=ISO_TILE_LINE_COLOR, thickness=4)

        return frame


    def get_static_frame(self):
        if not self.static_frame:
            self.static_frame = self._paint_isometric_static_frame()
        return self.static_frame

    def _paint_playground(self):
        return

    def _paint_large_pixel(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        return