import numpy as np
from typing import Dict, Tuple, List, Union
from dataclasses import dataclass, field

import cv2

from colony.characters.colony import Colony


# common settings
POP_PANE_COLOR: Union[int, Tuple[int, ...]] = 220
UNASSIGNED_CURVE_COLOR: Tuple[int, ...] = (255, 255, 255)
CURVE_THICKNESS: int = 1
THICK_CURVE_THICKNESS: int = 2
DATA_POINT_LIMIT: int = 128  # lines to draw is DATA_POINTS - 1

# stat type specific settings
POP_CURVE_COLOR: Tuple[int, ...] = (97, 52, 107)


@dataclass
class StatTracker:
    """
    A simple dataclass holding historical high values, and certain number of datapoints.
    """

    prev_high: int = 0
    data: List[int] = field(default_factory=lambda: [])  # queue
    color: Tuple[int, ...] = UNASSIGNED_CURVE_COLOR
    thickness: int = CURVE_THICKNESS


class PopulationCurve:
    """
    Plot a curve (more precisely, a series of discreted dots)
    """

    def __init__(self, width: int, height: int):
        """
        Now initialize formally the object
        """
        self.width: int = width
        self.height: int = height
        self.plottable_height: int = int(self.height * 0.90)
        self.line_spacing: int = int(self.width / DATA_POINT_LIMIT)

        self.population_tracker: StatTracker = StatTracker(color=POP_CURVE_COLOR)

    def normalized_height(self, value: float, tracker: StatTracker) -> int:
        """Get normalized value compared with record high."""
        return int(value / tracker.prev_high * self.plottable_height)

    def plot_curve_with_updated_point(
        self, frame: np.ndarray, point: int, tracker: StatTracker
    ):
        """
        Intake a new value and add to queue, then make a plot and using opencv lines.
        """
        # if reaches the max size, remove the first element
        if len(tracker.data) == DATA_POINT_LIMIT:
            tracker.data.pop(0)

        # append the new element
        tracker.data.append(point)

        # update high
        tracker.prev_high = max(tracker.prev_high, point)

        line_dots: List[Tuple[int, int]] = []
        for ri, value in enumerate(
            tracker.data[::-1]
        ):  # acquire position of each data point
            line_dots.append(
                (
                    self.width - self.line_spacing * ri - 1,
                    self.plottable_height - self.normalized_height(value, tracker),
                )
            )
        # draw polyline (in-place mutation)
        cv2.polylines(
            frame,
            [np.array(line_dots)],
            isClosed=False,
            color=tracker.color,
            thickness=tracker.thickness,
        )

    def draw_colony_curves(self, colony: Colony) -> np.ndarray:
        """Draw a series of curves by reading the current status from a colony instance."""
        # read values from colony instance
        population: int = colony.current_pop

        # build a blank array to draw curves on
        frame = np.full((self.height, self.width, 3), POP_PANE_COLOR, dtype=np.uint8)

        # add curves
        self.plot_curve_with_updated_point(
            frame, point=population, tracker=self.population_tracker
        )

        return frame
