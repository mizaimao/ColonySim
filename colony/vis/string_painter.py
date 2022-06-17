"""String painting class for adding strings to np arrays."""
from typing import Callable, Dict, List, Tuple, Union
import cv2
import numpy as np

POP_FONT: int = cv2.FONT_HERSHEY_DUPLEX
POP_TEXT_COLOR: Tuple[int, ...] = (100, 100, 100, 0)
POP_FONT_THICKNESS: int = 3


class StringPainter:
    """Adding text on the given frame."""

    def __init__(
        self,
        front_spaces: int = 1,
        line_spaces: int = 1,
        font: int = POP_FONT,
        text_color: Tuple[int, ...] = POP_TEXT_COLOR,
        text_thickness: int = POP_FONT_THICKNESS,
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
        self, frame: np.ndarray, line_id: int, string: str = None
    ):
        """Add a single line to frame and use line_id to find position."""
        if string is None:
            string = " "
        print("printing", string, "at", str((0, self.pixel_per_line * line_id)))
        print(frame.shape)
        cv2.putText(
            frame,
            " " * self.front_spaces + string,
            (0, self.pixel_per_line * line_id),  # position
            self.font,
            self.font_scalar,  # font and scale
            self.text_color,
            self.text_thickness,
        )

    def paint_lines(
        self,
        frame: np.ndarray,
        lines: Union[str, List[str]],
    ):
        """Paint strings to target frame. Each item in string list is a line.

        Args
            frame: target frame; in-place text addition
            lines: list of strings to put on frame
            font_scalar: font scalar
            front_spaces: spaces before text
            line_spaces: spaces between lines
        """
        if isinstance(lines, str):
            lines = [lines]

        if self.font_scalar is None:
            self.font_scalar = self.get_optimal_font_scale(width=frame.shape[1])
            line_count: int = len(lines)
            total_line_count: int = (
                line_count + (line_count - 1) * self.line_spaces
            )  # considering spaces
            self.pixel_per_line = int(frame.shape[0] / total_line_count)

        # add the top spacer
        self._paint_single_info_string(frame=frame, line_id=0)
        line_id: int = 1
        space_id: int = 0
        line: str = lines.pop(0)
        while lines:
            self._paint_single_info_string(frame=frame, line_id=line_id, string=line)
            line_id += 1
            while space_id % self.line_spaces != 0:
                self._paint_single_info_string(frame=frame, line_id=line_id)
                line_id += 1
            line = lines.pop(0)
        self._paint_single_info_string(frame=frame, line_id=line_id, string=line)
