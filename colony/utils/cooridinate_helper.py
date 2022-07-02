from typing import Tuple
import numpy as np
from typing import Dict, List, Tuple, Set
from colony.configs.map_generator.ref import PASSABLE

STD_MOVEMENTS: List[Tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]
DIAG_MOVEMENTS: List[Tuple[int, int]] = [(1, 1), (-1, -1), (1, -1), (-1, 1)]

def validate_coor(
        bitmap: np.ndarray,
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
        # check if this tile is occupied by terrain
        if not bitmap[y][x] in PASSABLE:
            return False
        # then check if this tile is occupied by other spores
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
    
    Returns
        list: path list from start to end, excluding start, including end.
            If no such path exist, an empyt list will be returned.
    """

    movements = STD_MOVEMENTS + (DIAG_MOVEMENTS if diagonal_move else [])
    height, width = bitmap.shape

    visited: Dict[Tuple[int, int], int] = {}
    queue: List[Tuple[int, int]] = [start + start]

    while queue:
        x, y, last_x, last_y = queue.pop(0)
        coor: Tuple[int, int] = x, y
        if coor in visited:
            continue
        visited[coor] = (last_x, last_y)
        if coor == end:  # reached destination
            break
        for dx, dy in movements:
            new_coor: Tuple[int, int] = (coor[0] + dx, coor[1] + dy)
            if validate_coor(
                bitmap=bitmap, 
                x_high=width,
                y_high=height,
                coor=new_coor,
                step=step,
                spore_overlapping=spore_overlapping
            ):
                # valid tile, then add it to BFS queue
                queue.append(new_coor + (x, y))

    # trace back to get a path
    # end was never reached, therefore no path was found
    if end not in visited:
        return []
    # else, trace back from end to start
    path: List[Tuple[int, int]] = [end]
    last_coor = visited[end]
    while last_coor != start:
        path.append(last_coor)
        last_coor = visited[last_coor]
    return path[::-1]
