"""Helper functions for color-related tasks.
"""
from typing import List, Tuple, Union

def shift_color(color: Tuple[int, ...], shift: Union[int, Tuple[int, ...]], shift_alpha: bool = False):
    if isinstance(shift, Tuple):
        assert len(shift) == len(
            color
        ), "color and shift should have the same amout of channels."
        _new_color_0: List[int] = [sum(c + s) for c, s in zip(color, shift)]
    else:
        if len(color) == 3:
            _new_color_0 = [c + shift for c in color]
        elif len(color) == 4:
            if shift_alpha:
                _new_color_0 = [c + shift for c in color]
            else:
                _new_color_0 = [c + shift for c in color[:-1]] + [color[-1]]
        else:
            raise ValueError("Color input must be of 3 or 4 channels.")
    _new_color_2: List[int] = []
    for c in _new_color_0:
        if c > 255:
            _new_color_2.append(255)
        elif c < 0:
            _new_color_2.append(0)
        else:
            _new_color_2.append(c)

    return tuple(_new_color_2)