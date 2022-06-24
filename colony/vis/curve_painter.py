import numpy as np
from typing import Dict, Tuple, List, Union
from dataclasses import dataclass, field

import cv2

from colony.characters.colony import Colony


# common settings
POP_PANE_COLOR: Union[int, Tuple[int, ...]] = 230
UNASSIGNED_CURVE_COLOR: Tuple[int, ...] = (255, 255, 255)
CURVE_THICKNESS: int = 1
THICK_CURVE_THICKNESS: int = 2
DATA_POINT_LIMIT: int = 128  # lines to draw is DATA_POINTS - 1

# stat type specific settings
POP_CURVE_COLOR: Tuple[int, ...] = (97, 52, 107)
FOOD_CURVE_COLOR: Tuple[int, ...] = (60, 30, 159)
RES_21_CURVE_COLOR: Tuple[int, ...] = (73, 116, 164)
RES_22_CURVE_COLOR: Tuple[int, ...] = (141, 140, 136)
RES_23_CURVE_COLOR: Tuple[int, ...] = (206, 204, 202)


@dataclass
class StatTracker:
    """
    A simple dataclass holding historical high values, and certain number of datapoints.
    """

    prev_high: int = 1
    data: List[int] = field(default_factory=lambda: [])  # queue
    color: Tuple[int, ...] = UNASSIGNED_CURVE_COLOR
    thickness: int = CURVE_THICKNESS


class CurvePainter:
    """
    Plot a curve (more precisely, a series of discreted dots)
    """

    def __init__(self, width: int, height: int):
        """
        Now initialize formally the object
        """
        self.width: int = width
        self.height: int = height
        self.plottable_height: float = self.height * 0.95
        self.line_spacing: float = self.width / (DATA_POINT_LIMIT - 1)

        self.population_tracker: StatTracker = StatTracker(color=POP_CURVE_COLOR)
        self.food_tracker: StatTracker = StatTracker(color=FOOD_CURVE_COLOR)
        self.res_21_tracker: StatTracker = StatTracker(color=RES_21_CURVE_COLOR)
        self.res_22_tracker: StatTracker = StatTracker(color=RES_22_CURVE_COLOR)
        self.res_23_tracker: StatTracker = StatTracker(color=RES_23_CURVE_COLOR)


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
                    self.width - int(self.line_spacing * ri),
                    #self.plottable_height - self.normalized_height(value, tracker),
                    self.height - self.normalized_height(value, tracker)
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

        food: int = colony.storage.res[11]
        res_21: int = colony.storage.res[21]
        res_22: int = colony.storage.res[22]
        res_23: int = colony.storage.res[23]

        # build a blank array to draw curves on
        frame = np.full((self.height, self.width, 3), POP_PANE_COLOR, dtype=np.uint8)
        
        # add curves
        self.plot_curve_with_updated_point(
            frame, point=population, tracker=self.population_tracker
        )
        self.plot_curve_with_updated_point(
            frame, point=food, tracker=self.food_tracker
        )
        self.plot_curve_with_updated_point(
            frame, point=res_21, tracker=self.res_21_tracker
        )
        self.plot_curve_with_updated_point(
            frame, point=res_22, tracker=self.res_22_tracker
        )
        self.plot_curve_with_updated_point(
            frame, point=res_23, tracker=self.res_23_tracker
        )

        return frame
