"""String painting class for adding strings to np arrays."""
from typing import Callable, Dict, List, Tuple, Union
import cv2
import numpy as np

from colony.characters.colony import Colony
from colony.utils.info_manager import InfoManager
from colony.utils.color_helpers import shift_color

POP_FONT: int = cv2.FONT_HERSHEY_SIMPLEX
POP_COLOR: Tuple[int, ...] = (100, 100, 100, 0)
POP_THICKNESS: int = 3

INFO_FONT: int = cv2.FONT_HERSHEY_SIMPLEX
INFO_COLOR: Tuple[int, ...] = (100, 100, 100, 0)
INFO_THICKNESS: int = 1
INFO_DECAY: int = 20


class StringPainter:
    """Adding text on the given frame."""

    def __init__(
        self,
        front_spaces: int = 1,
        line_spaces: int = 1,
        font: int = POP_FONT,
        text_color: Tuple[int, ...] = POP_COLOR,
        text_thickness: int = POP_THICKNESS,
    ):
        """
        Two lazy properties will be calculated when the first frame is parsed. Assuming the rest of frames
        will come in identical shapes.
        """
        self.front_spaces: int = front_spaces
        self.line_spaces: int = line_spaces
        self.font: int = font
        self.text_color: Tuple[int, ...] = text_color
        self.text_thickness: int = text_thickness

        # lazy properties
        self.font_scalar: float = None
        self.pixel_per_line: int = None

    @staticmethod
    def get_optimal_font_scale(width: int, text: str = None):
        if not text:
            text = " " * 30
        for scale in range(59, -1, -1):
            textSize = cv2.getTextSize(
                text,
                fontFace=cv2.FONT_HERSHEY_DUPLEX,
                fontScale=scale / 10,
                thickness=1,
            )
            if textSize[0][0] <= width:
                return scale / 10
        return 1

    def _paint_single_info_string(
        self,
        frame: np.ndarray,
        line_id: int,
        string: str = None,
        color: Tuple[int, ...] = None,
    ):
        """Add a single line to frame and use line_id to find position."""
        if string is None:
            string = " "

        cv2.putText(
            frame,
            " " * self.front_spaces + string,
            (0, self.pixel_per_line * line_id),  # position
            self.font,
            self.font_scalar,  # font and scale
            self.text_color if color is None else color,
            self.text_thickness,
        )

    def paint_lines(
        self,
        frame: np.ndarray,
        lines: Union[str, List[str]],
        line_id_override: int = None,
        color_override: Tuple[int, ...] = None,
    ) -> int:
        """Paint strings to target frame. Each item in string list is a line.

        Args
            frame: target frame; in-place text addition
            lines: list of strings to put on frame

        Returns
            int: the next line id after printing; such that when this function is consecutively
                called, the next instance will find the right location to print
        """
        if isinstance(lines, str):
            lines = [lines]
        color: Tuple[int, ...] = (
            self.text_color if color_override is None else color_override
        )

        if self.font_scalar is None:
            self.font_scalar = self.get_optimal_font_scale(width=frame.shape[1])
            line_count: int = len(lines)
            total_line_count: int = (
                line_count + (line_count - 1) * self.line_spaces
            )  # considering spaces
            self.pixel_per_line = int(frame.shape[0] / total_line_count)

        # add the top spacer
        self._paint_single_info_string(frame=frame, line_id=0)
        line_id: int = 1 if line_id_override is None else line_id_override

        if not lines:  # nothing to print, early return
            return line_id

        space_id: int = 0
        line: str = lines.pop(0)
        while lines:
            self._paint_single_info_string(
                frame=frame, line_id=line_id, string=line, color=color
            )
            line_id += 1
            while space_id % self.line_spaces != 0:
                self._paint_single_info_string(
                    frame=frame, line_id=line_id, color=color
                )
                line_id += 1
            line = lines.pop(0)
        self._paint_single_info_string(
            frame=frame, line_id=line_id, string=line, color=color
        )
        return line_id + 1

    def paint_lines_decaying(
        self,
        frame: np.ndarray,
        line_lists: List[List[str]],
        line_count_override: int,
    ):
        """Paint strings to target frame. Contains multiple sets of lines. Each set will
        have a shallower color than the previous set.

        Args
            frame: target frame; in-place text addition
            lines: list of lists of strings to put on frame
        """
        if self.font_scalar is None:
            self.font_scalar = self.get_optimal_font_scale(
                width=frame.shape[1], text=" " * 200
            )
            line_count: int = line_count_override
            total_line_count: int = (
                line_count + (line_count - 1) * self.line_spaces
            )  # considering spaces
            self.pixel_per_line = int(frame.shape[0] / total_line_count)

        line_id: int = 1
        color = INFO_COLOR

        for i, lines in enumerate(line_lists):
            line_id = self.paint_lines(
                frame=frame,
                lines=lines,
                line_id_override=line_id,
                color_override=shift_color(color, INFO_DECAY * i),
            )


def add_info_to_main_pane(
    painter: StringPainter,
    colony: Colony,
    frame: np.ndarray,
    max_rows: int = 20,
    steps: int = 5,
):
    """Print game info to main pane (or any frame).
    Args
        painter: painter from caller; can be None so that this function will create one
            and return it
        colony: a Colony instance, who should contain an InfoManager instance, and the
            function will read info strings saved insiide
        frame: the array we want to print on
        max_rows: upper limit of maximum rows on display
        steps: most recent set of info strings will be shown in most heavy color, and
            the less recent ones will have shallower colors. This arg controls how far
            back we want to print info.
    """
    if painter is None:
        painter = StringPainter(
            front_spaces=1,
            line_spaces=1,
            font=INFO_FONT,
            text_color=INFO_COLOR,
            text_thickness=INFO_THICKNESS,
        )

    assert (
        not colony.printer.info_stack
    ), "Colony info logger should be empty when printing strings to main frame."
    line_lists = colony.printer.info_history[-steps:]  # last serveral steps
    painter.paint_lines_decaying(frame, line_lists[::-1],line_count_override=max_rows)

    return painter
