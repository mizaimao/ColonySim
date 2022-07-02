from typing import Tuple
import numpy as np
from typing import Dict, List, Tuple, Set

STD_MOVEMENTS = List[Tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIAG_MOVEMENTS = List[Tuple[int, int]] = [(1, 1), (-1, -1), (1, -1), (-1, 1)]

def validate_coor(
        x_high: int,
        y_high: int,
        coor: Tuple[int, int],
        step: Dict[Tuple[int, int], List[int]],
        x_low: int = 0,
        y_low: int = 0,
        spore_overlapping: bool = False,
    ):
    """
    To verify if the generated coor are inside map
    """
    x, y = coor
    # first level check if coor is inside map
    if x_low <= x < x_high and y_low <= y < y_high:
        # then check if coor is not overlapping
        if not spore_overlapping and coor in step:
            return False
        return True
    return False 

def bfs(
        bitmap: np.ndarray,
        start: Tuple[int, int], 
        end: Tuple[int, int],
        step: Dict[Tuple[int, int], List[int]] = {},
        diagonal_move: bool = False,
        spore_overlapping: bool = False
    ) -> List[Tuple[int, int]]:
    """BFS path finding.
    Args
        bitmap: tile map.
        start: starting location.
        end: destination tile.
        step: spore step to check if there are overlapping.
        diagonal_move: allow movement in diagonally.
        spore_overlapping: whether to allow spore overlapping.
    """
    movements = STD_MOVEMENTS + DIAG_MOVEMENTS if diagonal_move else []

    x_high, y_high = bitmap.shape

    visited: Dict[Tuple[int, int], int] = {}
    queue: List[Tuple[int, int]] = [start]


    while queue:
        current: Tuple[int, int] = queue.pop(0)
        for dx, dy in movements:
            if validate_coor()





    return