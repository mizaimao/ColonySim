from typing import Tuple
import numpy as np
from typing import Dict, List, Tuple, Set


def validate_coor(
        x_low: int,
        x_high: int,
        y_low: int,
        y_high: int,
        coor: tuple,
        step: dict
    ):
    """
    To verify if the generated coor are inside map
    """
    x, y = coor
    if x_low <= x < x_high and y_low <= y < y_high and ((x, y) not in step):
        return True
    return False 

def bfs(
        bitmap: np.ndarray,
        start: Tuple[int, int], 
        end: Tuple[int, int],
        step: Dict[Tuple[int, int], List[int]] = {}
    ) -> List[Tuple[int, int]]:
    """Standard BFS returnning path."""

    visited: Dict[Tuple[int, int], int] = {}
    queue: List[Tuple[int, int]] = [start]



    while queue:
        current: Tuple[int, int] = queue.pop(0)




    return