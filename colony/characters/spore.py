from dataclasses import dataclass
from typing import Tuple

FOOD_SPEED: Tuple[int, ...] = (2, 4, 8, 12)
RES21_SPEED: Tuple[int, ...] = (1, 2, 3, 4)
RES22_SPEED: Tuple[int, ...] = (1, 2, 3, 4)
RES23_SPEED: Tuple[int, ...] = (0, 2, 3, 4)


@dataclass
class Spore:
    sid: int
    sex: int
    age: int
    health: int
