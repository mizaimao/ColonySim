import numpy as np

from abc import ABC, abstractmethod
from typing import Tuple, Union

from colony.configs.map_generator.ref import map_ref
from colony.configuration import visual_cfg

STAGE_BACKGROUND: Union[int, Tuple[int, int, int]] = visual_cfg.stage_background


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
