from typing import Tuple
import numpy as np
from typing import Dict, List, Tuple, Set
from colony.configs.map_generator.ref import BUILDABLE, PASSABLE
from colony.characters.terrain import TerrainManager

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

class LocationFinder:
    def __init__(
            self,
            terrain_man: TerrainManager,
            combined_step = {},
            building_step = {},
            rng: np.random.RandomState = np.random.RandomState(720),  
        ):
        self.terrain_man: TerrainManager = terrain_man
        # width and height to calculate random locations
        self.height, self.width = self.terrain_man.bitmap.shape
        self.rng = rng
        # cached available locations; used for randomly getting available tiles.
        #   since avalialbe locations will change overtime, each time a new building was
        #   requested to be built on random locations, this list will be reset
        self.available_tiles: List[Tuple[int, int]] = []
        self.available_tiles_generated: bool = False
        self.combined_step = combined_step
        self.building_step = building_step
    
    def update_steps(self, combined_step, building_step):
        self.combind_step = combined_step
        self.building_step = building_step

    def get_random_coor_naive(self) -> Tuple[int, int]:
        """Roll a pair of x y to form a random coor."""
        x: int = self.rng.randint(low=0, high=self.width)
        y: int = self.rng.randint(low=0, high=self.height)
        return x, y
    
    def get_random_coor(self) -> Tuple[int, int]:
        """
        Roll a pair of coor from unoccupied tiles.
        We first find all available tiles and cache them into a class variable,
        and then randomly choose one. If that one doesn't work (like 2x1 buildings),
        this function will be called again until we exhaust all options.

        Returns
            Tuple[int, int] or None: a random location where the building can potentially
                be built; or None if there is no such location.
        """
        # under two situations when this variable is empty:
        # 1. the function was first called
        # 2. we exhausted all tiles and still could not find a suitable one
        if len(self.available_tiles) == 0:
            if self.available_tiles_generated:  # case 2
                return None
            # case 1
            for x in range(self.width):
                for y in range(self.height):
                    coor: Tuple[int, int] = (x, y)
                    if coor not in self.combined_step and \
                        coor not in self.building_step:
                        self.available_tiles.append(coor)
            self.rng.shuffle(self.available_tiles)
            self.available_tiles_generated = True
        # return a random index in cache
        return self.available_tiles.pop()

    def tile_buildable(self, loc: Tuple[int, int]) -> bool:
        """Checks if the given location is buildable. First checks if there are exisiting spores
        on this tile, and then checks if the terrain allows."""
        if (loc not in self.combined_step) and \
            (self.terrain_man.bitmap[loc[1]][loc[0]] in BUILDABLE):
            return True
        return False

    def validate_loc_and_ori(self, loc: Tuple[int, int], size: Tuple[int, int]) -> bool:
        """Validate whether the building can be built with given location and orientation."""
        x, y = loc
        for y_extend in range(size[1]):
            for x_extend in range(size[0]):
                print(x + x_extend, y + y_extend)
                if not self.tile_buildable((x + x_extend, y + y_extend)):
                    return False
        return True
    
    def build_at_location_with_random_orientation(
            self,
            loc: Tuple[int, int],
            sizes: List[Tuple[int, int]]
        ) -> int:
        """The location is specified, but no orientation was given.
        The function will enumerate possible orientations from the variable sizes,
        and randomly choose an available one.

        Args
            loc: location of upper left corner tile of building.
            sizes: a list of building sizes. This information already be defined in
                tileset yaml and loaded by image loader/manager.
        
        Returns
            int: index of orientation of choice. The choice may come as a result of random
                selection, or it is the only available choice at that tile.
        """
        assert len(sizes), "Given building does not contain size information."
        available_indices: List[int] = []
        for i, size in enumerate(sizes):
            if self.validate_loc_and_ori(loc=loc, size=size):
                available_indices.append(i)
        if not available_indices:  # zero-size means the building cannot be built
            return -1
        return self.rng.choice(available_indices)

    def build_with_random_loc_and_random_ori(
            self,
            avail_ori: List[Tuple[int, int]],
        ):
        """Get a random location and random orientation."""
        loc: Tuple[int, int] = None
        ori: int = -1
        random_loc: Tuple[int, int] = self.get_random_coor()
        while random_loc is not None:
            random_ori: int = self.build_at_location_with_random_orientation(
                loc=random_loc, sizes=avail_ori
            )
            if random_ori == -1:  # location and ori don't work, then try again
                random_loc = self.get_random_coor()
            else:  # building can be built with this pair of random loc and ori
                loc = random_loc
                ori = random_ori
                break
        self.available_tiles.clear()
        self.available_tiles_generated = False
        return loc, ori

    def build_with_random_loc_and_given_ori(
            self,
            size: Tuple[int, int]
        ):
        """Get a random loc for given orientation."""
        loc: Tuple[int, int] = None
        random_loc: Tuple[int, int] = self.get_random_coor()
        while random_loc is not None:
            if self.validate_loc_and_ori(loc=random_loc, size=size):
                loc = random_loc
                break
            else:
                random_loc = self.get_random_coor()
        self.available_tiles.clear()
        self.available_tiles_generated = False
        return loc

    def perform_building_physical_checks(
            self,
            loc: Tuple[int, int] = None,
            orientation: int = None,
            avail_ori: List[Tuple[int, int]] = [],
        ):
        """Perform physical checks on request building location and orientation (case 0).
        
        There are also cases when location or orientation not specified:
        1. If neither were given, then chose a random location and random orientation.
        2. If only location was given, then check all possible orientations and
            randomly select one.
        3. If only orientation was given, then choose a random location (or keep trying
            until all tiles are exhauseted)
        """
        # two key variables for building
        buildable_loc: Tuple[int, int] = None
        buildbale_ort: int = -1  # -1 for invalid

        # case 0: when both loc and orientation are given
        if (loc is not None) and (orientation is not None):
            if self.validate_loc_and_ori(loc, avail_ori[orientation]):
                buildable_loc = loc
                buildbale_ort = orientation
        # case 1: neither were given
        elif loc is None:
            if orientation is None:
                buildable_loc, buildbale_ort = \
                    self.build_with_random_loc_and_random_ori(avail_ori=avail_ori)
            # case 3: only orientation was given
            else:
                buildable_loc = \
                    self.build_with_random_loc_and_given_ori(size=avail_ori[orientation])
                buildbale_ort = orientation
        # case 2: only location was given
        else:
            buildable_loc = loc
            buildbale_ort = self.build_at_location_with_random_orientation(
                loc=loc, sizes=avail_ori
            )
        return buildable_loc, buildbale_ort
