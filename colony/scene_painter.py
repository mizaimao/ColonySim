"""Painter functions to draw 2D or isometric views of upper panel.
"""
from abc import ABC, abstractmethod
from typing import Callable, List, Tuple, Union
from black import out
import cv2
import numpy as np
from math import sqrt
from configs.map_generator.ref import map_ref

# artifacial upper and lower blanks
ISO_UPPER: float = 0.05  # ratio to frame height
ISO_LOWER: float = 0.05

ISO_TILE_HEIGHT: float = 1.0  # raito to mega pixel size
ISO_TILE_GRID_LINE_THICKNESS: int = 4
ISO_TILE_WIDTH_SCALAR: float = sqrt(3)
ISO_TILE_HEIGHT_SCALAR: float = 1.0
ISO_TILE_LINE_COLOR: Tuple[float, ...] = (100, 100, 100)
ISO_TILE_UPPER_LEFT_COLOR_SHIFT: Union[int, Tuple[int, ...]] = -60
ISO_TILE_UPPER_right_COLOR_SHIFT: Union[int, Tuple[int, ...]] = -30
ISO_TILE_OUTLINE_THICKNESS: int = 1
#ISO_TILE_OUTLINE_COLOR: Tuple[float, ...] = (150, 150, 150)
ISO_TILE_OUTLINE_COLOR: Tuple[float, ...] = (210, ) * 3

DIRT_COLOR: Tuple[float, ...] = (183, 118, 155)  # BGR for sake of opencv

# no alpha channel
STAGE_BACKGROUND: Union[int, Tuple[int, int, int]] = (202, 193, 103)# color for stage level background


class ColonyView(ABC):
    """Upper viewing panel drawer."""

    def __init__(
        self, width: int, height: int, frame_width: int, frame_height: int, bitmap
    ):
        self.width: int = width
        self.height: int = height
        self.frame_height: int = frame_height
        self.frame_width: int = frame_width
        self.bitmap = bitmap
        self.multiplier: float = None
        self.static_frame: np.ndarray = None

    @abstractmethod
    def get_static_frame(self):
        """Paint the starge background, and calclulate variables needed for playground.
        Stage background is the back-most layer, and playground is the space where each dot moves around.
        """
        pass

    @abstractmethod
    def paint_playground(self):
        """Paint playground."""
        pass

    @abstractmethod
    def paint_large_pixel(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Add individual large "pixels" onto scene/playground."""
        pass


class ColonyView2D(ColonyView):
    def __init__(
        self, width: int, height: int, frame_width: int, frame_height: int, bitmap
    ):
        super().__init__(width, height, frame_width, frame_height, bitmap)

        # if colony shape is different from viewer shape, some spaces must be padded.
        self.left_blank: int = 0  # blank space on leftside
        self.top_blank: int = 0  # blank space on top

        # because we now separated viwer shape and colony shape, there should be a value we use to map colony dots to
        # viewer.
        self._figure_out_multiplier()

    def _figure_out_multiplier(self):
        """To figure out a scalar that we can use to map individual dots to playground by giving them a size."""
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
        """Paint the background."""
        if not self.static_frame:
            self.static_frame = np.full(
                (self.frame_height, self.frame_width, 3),
                STAGE_BACKGROUND,
                dtype=np.uint8,
            )
        return self.static_frame

    def paint_playground(self):
        """Paint playground."""
        for y in range(len(self.bitmap)):
            for x in range(len(self.bitmap[0])):
                color = map_ref[self.bitmap[y][x]][-1]
                self.paint_large_pixel(self.static_frame, y, x, color)

    def paint_large_pixel(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Paint a big pixel element on the given frame."""
        x_start = int(x * self.multiplier) + self.left_blank
        x_end = int((x + 1) * self.multiplier) + self.left_blank
        y_start = int(y * self.multiplier) + self.top_blank
        y_end = int((y + 1) * self.multiplier) + self.top_blank

        frame[y_start:y_end, x_start:x_end] = color


class ColonyViewIso(ColonyView):
    def __init__(
        self, width: int, height: int, frame_width: int, frame_height: int, bitmap
    ):
        assert (
            width == height
        ), f"Isometric view supports only square playground, got {(width, height)}"
        super().__init__(width, height, frame_width, frame_height, bitmap)

        # if colony shape is different from viewer shape, some spaces must be padded.
        self.left_blank: int = 0  # blank space on leftside
        self.top_blank: int = 0  # blank space on top

        # multiplier used for mapping isometric tile sizes
        self.multiplier_iso: float = 0

        # isometric tile shape (lenght of diagnoals, not sides of these dimond-shaped objects)
        self.tile_width: float = 0
        self.tile_height: float = 0

        # fake-3D gets a Z metric, some depth goes above a tile and the rest goes blow
        self.tile_upper_depth: float = 0
        self.tile_lower_depth: float = 0
        # offsets from edges, will be calculated later
        self.width_offset: float = 0
        self.height_offset: float = 0

        # figure out multiplier when projecting into isometric spaces
        self._figure_out_multiplier()

    def _figure_out_multiplier(self):
        """Here more than a simple multiplier was calculated. This is becasue the invovement of isometric mapping."""
        # this "traditional" multiplier set is used to scale UI stuffs, like it does in 2D version.
        multiplier_x: float = self.frame_width / self.width
        multiplier_y: float = self.frame_height / self.height
        self.multiplier = min(multiplier_x, multiplier_y)

        # this isotromic multiplier set is used to draw tiles
        # calculate artificial Y blanks, which are some reserved spaces at top and bottom (for fake hight in the future)
        deduced_y_space: float = self.frame_height * (ISO_UPPER + ISO_LOWER)
        multiplier_x_iso: float = self.frame_width / (
            self.width * ISO_TILE_WIDTH_SCALAR
        )
        multiplier_y_iso: float = (self.frame_height - deduced_y_space) / (
            self.height * ISO_TILE_HEIGHT_SCALAR
        )
        self.multiplier_iso = min(multiplier_x_iso, multiplier_y_iso)

        # calculate size of each tile. Not their sides but more like diagonals of the dimond shapes.
        self.tile_width = self.multiplier_iso * ISO_TILE_WIDTH_SCALAR
        self.tile_height = self.multiplier_iso * ISO_TILE_HEIGHT_SCALAR

        # figure out blank paddings at top and left
        self.left_blank = int((self.frame_width - self.tile_width * self.width) / 2)
        self.top_blank = int((self.frame_height - self.tile_height * self.height) / 2)

        # height offset is needed to "shift" pixles to right by half of playground width
        # different maths requires x-shifting, but it's not the case here
        self.width_offset = 0 + self.left_blank
        self.height_offset = self.tile_height * self.height / 2 + self.top_blank

        # figure out tile depth above and below surface
        # simple case now, just cut them into halves
        self.tile_upper_depth = self.tile_height / 2
        self.tile_lower_depth = self.tile_height / 2

    def _get_iso_coor(self, x: float, y: float):
        """Convert bitmap coordinates to isometric coordinates.
        OpenCV draw lines by using integer indices (of course).

        This projecting scheme makes dot (0, 0) or the upper left corner mapped to the very left spot.
        """
        # this isometric mapping requires y-shifting
        new_x: int = int(
            (x * self.tile_width / 2) + (y * self.tile_width / 2) + self.width_offset
        )
        new_y: int = int(
            (y * self.tile_height / 2) - (x * self.tile_height / 2) + self.height_offset
        )
        return (new_x, new_y)

    def _paint_grid_lines(self, frame: np.ndarray):
        """Not used. 
        Draw grid lines for debugging purposes.
        """
        # add x grid lines to frame
        # from (0, Y0) to (x, Y0) until (0, Yy) to (x, Yy)
        for y in range(self.height + 1):
            start_point = self._get_iso_coor(0, y)
            end_point = self._get_iso_coor(self.width, y)
            cv2.line(
                frame,
                start_point,
                end_point,
                color=ISO_TILE_LINE_COLOR,
                thickness=ISO_TILE_GRID_LINE_THICKNESS,
            )
        # add y grid lines to frame
        # from (X0, 0) to (X0, y) until (Xx, 0) to (Xx, y)
        for x in range(self.width + 1):
            start_point = self._get_iso_coor(x, 0)
            end_point = self._get_iso_coor(x, self.height)
            cv2.line(
                frame,
                start_point,
                end_point,
                color=ISO_TILE_LINE_COLOR,
                thickness=ISO_TILE_GRID_LINE_THICKNESS,
            )

    def _paint_isometric_static_frame(self):
        # create a blank background
        frame = np.full(
            (self.frame_height, self.frame_width, 3), STAGE_BACKGROUND, dtype=np.uint8
        )
        return frame

    def get_static_frame(self):
        """Paint background and do essential calculations."""
        if not self.static_frame:
            self.static_frame = self._paint_isometric_static_frame()
        return self.static_frame

    def paint_playground(self):
        """Paint the playground."""
        assert (
            self.static_frame is not None
        ), "Call get_static_frame first to paint a static frame."

        # the loop order need to be modifed
        for y in range(len(self.bitmap)):
            for x in range(len(self.bitmap[0]) - 1, 0 - 1, -1):
                color = map_ref[self.bitmap[y][x]][-1]
                self.paint_large_pixel(self.static_frame, y, x, color, background=True)
        return

    def paint_large_pixel_plane(self, frame: np.ndarray, x: int, y: int, color: Tuple):
        """Draw mega pixel without depth info, just overlay them on a plane"""
        # the function adds blanks automatically
        # four corners of each tile
        ul: Tuple(int, int) = self._get_iso_coor(x, y)
        ur: Tuple(int, int) = self._get_iso_coor(x + 1, y)
        ll: Tuple(int, int) = self._get_iso_coor(x, y + 1)
        lr: Tuple(int, int) = self._get_iso_coor(x + 1, y + 1)
        contours = np.array([ul, ll, lr, ur])
        cv2.fillPoly(frame, pts=[contours], color=color)

    @staticmethod
    def _shift_color(color: Tuple[int, ...], shift: Union[int, Tuple[int, ...]]):
        if isinstance(shift, Tuple):
            assert len(shift) == len(
                color
            ), "color and shift should have the same amout of channels."
            _new_color_0: List[int] = [sum(c + s) for c, s in zip(color, shift)]
        else:
            _new_color_0 = [c + shift for c in color]
        _new_color_2: List[int] = []
        for c in _new_color_0:
            if c > 255:
                _new_color_2.append(255)
            elif c < 0:
                _new_color_2.append(0)
            else:
                _new_color_2.append(c)

        return tuple(_new_color_2)

    @staticmethod
    def _draw_tile_outlines(frame: np.ndarray, contours: np.ndarray):
            cv2.line(frame, contours[0], contours[1], ISO_TILE_OUTLINE_COLOR, ISO_TILE_OUTLINE_THICKNESS)
            cv2.line(frame, contours[1], contours[2], ISO_TILE_OUTLINE_COLOR, ISO_TILE_OUTLINE_THICKNESS)
            cv2.line(frame, contours[2], contours[3], ISO_TILE_OUTLINE_COLOR, ISO_TILE_OUTLINE_THICKNESS)
            cv2.line(frame, contours[3], contours[0], ISO_TILE_OUTLINE_COLOR, ISO_TILE_OUTLINE_THICKNESS)

    def paint_large_pixel(
        self,
        frame: np.ndarray,
        x: int,
        y: int,
        color: Tuple,
        background: bool = False,
        outline: bool = True,
    ):
        """Draw mega pixles with depth inofmration. There will be five regions for each tile now.
        1. The surface of tile, which needs an Y offset to elevate from ground; we will use self.tile_upper_depth
        2. Elevated left side of a tile;
        3. Elevated right side of a tile;
        4. Underground left side of a tile; (only displays when x==0)
        5. Underground right side of a tile;  (only displays when y==Y)

        Background tiles are painted a bit differently:
        1. Depth are a bit shallower
        2. Only show depth when x==0 and y==Y

        Tile outline applies only to player/mimic/whatever-individual tiles, not backgrounds tiles.
        Some lines are overlapping. So different sides will have different number of line drawing statements.
        """
        upper_depth_shifter: int = int(self.tile_upper_depth)
        upper_depth_shifter_half = int(upper_depth_shifter / 2)

        # four original corners of each tile
        ul: Tuple(int, int) = self._get_iso_coor(x, y)
        ur: Tuple(int, int) = self._get_iso_coor(x + 1, y)
        ll: Tuple(int, int) = self._get_iso_coor(x, y + 1)
        lr: Tuple(int, int) = self._get_iso_coor(x + 1, y + 1)

        shifter: Tuple[int, int] = (0, upper_depth_shifter)
        half_shifter: Tuple[int, int] = (0, upper_depth_shifter_half)
        if background:  # background has shallower depth (half of a tile)
            shifter = (0, upper_depth_shifter_half)
            half_shifter = (0, 0)

        # surface of a tile ??? why a positive number causing it shift below ???
        contours: np.ndarray = np.array([ul, ll, lr, ur]) - shifter
        cv2.fillPoly(frame, pts=[contours], color=color)
        if outline:
            self._draw_tile_outlines(frame, contours)

        # elevated left side
        if (not background) or (x == 0):
            contours = np.array([ul, ll, ll, ul]) - [shifter, shifter, half_shifter, half_shifter]
            cv2.fillPoly(
                frame,
                pts=[contours],
                color=self._shift_color(color, ISO_TILE_UPPER_LEFT_COLOR_SHIFT),
            )
            if outline:
                self._draw_tile_outlines(frame, contours)

        # elevated right side
        if (not background) or (y == self.height - 1):
            contours = np.array([ll, lr, lr, ll]) - [shifter, shifter, half_shifter, half_shifter]
            cv2.fillPoly(
                frame,
                pts=[contours],
                color=self._shift_color(color, ISO_TILE_UPPER_right_COLOR_SHIFT),
            )
            if outline:
                self._draw_tile_outlines(frame, contours)

        # underground left side
        if background and (x == 0):
            contours = np.array([ul, ll, ll, ul]) + [shifter, shifter, half_shifter, half_shifter]
            cv2.fillPoly(
                frame,
                pts=[contours],
                color=self._shift_color(DIRT_COLOR, ISO_TILE_UPPER_LEFT_COLOR_SHIFT),
            )
            if outline:
                self._draw_tile_outlines(frame, contours)


        # underground right side
        if background and (y == self.height - 1):
            contours = np.array([ll, lr, lr, ll]) + [shifter, shifter, half_shifter, half_shifter]
            cv2.fillPoly(
                frame,
                pts=[contours],
                color=self._shift_color(DIRT_COLOR, ISO_TILE_UPPER_LEFT_COLOR_SHIFT),
            )
            if outline:
                self._draw_tile_outlines(frame, contours)
