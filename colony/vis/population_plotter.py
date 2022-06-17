import numpy as np
from typing import Tuple, List, Union

import cv2

POP_PANE_COLOR: Union[int, Tuple[int, ...]] = 220
POP_CURVE_COLOR: Tuple[int, ...] = (80, 30, 00)
CURVE_THICKNESS: int = 1
THICK_CURVE_THICKNESS: int = 2
DATA_POINTS: int = 128  # lines to draw is DATA_POINTS - 1


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
        self.line_spacing: int = int(self.width / DATA_POINTS)

        self.prev_high = 1
        self.data = []  # queue

    def update_and_plot_dot_plot(self, point: int):
        """
        Intake a new value and add to queue, then make a plot and
        and return it. This adds simple dots on the plot.
        """
        # if reaches the max size, remove the first element
        if len(self.data) == DATA_POINTS:
            self.data.pop(0)

        # append the new element
        self.data.append(point)

        # update high
        self.prev_high = max(self.prev_high, point)

        # iterate through the heights in reversed order and plot dots
        plot = np.full((self.height, self.width, 3), POP_PANE_COLOR, dtype=np.uint8)
        for ri, value in enumerate(self.data[::-1]):  # reversed index
            plot[
                self.plottable_height
                - int(value / self.prev_high * self.plottable_height),
                self.width - ri - 1,
            ] = POP_CURVE_COLOR

        return plot

    def normalized_height(self, value: float) -> int:
        """Get normalized value compared with record high."""
        return int(value / self.prev_high * self.plottable_height)

    def update_and_plot(self, point: int):
        """
        Intake a new value and add to queue, then make a plot and
        and return it. Draws lines on as plot.
        """
        # if reaches the max size, remove the first element
        if len(self.data) == DATA_POINTS:
            self.data.pop(0)

        # append the new element
        self.data.append(point)

        # update high
        self.prev_high = max(self.prev_high, point)

        # iterate through the heights in reversed order and plot dots
        plot = np.full((self.height, self.width, 3), POP_PANE_COLOR, dtype=np.uint8)

        line_dots: List[Tuple[int, int]] = []
        for ri, value in enumerate(
            self.data[::-1]
        ):  # acquire position of each data point
            line_dots.append(
                (
                    self.width - self.line_spacing * ri - 1,
                    self.plottable_height - self.normalized_height(value),
                )
            )
        # draw polyline
        cv2.polylines(
            plot,
            [np.array(line_dots)],
            isClosed=False,
            color=POP_CURVE_COLOR,
            thickness=CURVE_THICKNESS,
        )
        return plot
