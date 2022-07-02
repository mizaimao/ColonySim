"""Building objects for colony."""
from curses import termattrs
from dataclasses import dataclass, field
from distutils.command.build import build
from tkinter import BitmapImage
from typing import Any, List, Dict, Set, Tuple, Optional
from matplotlib.style import available

import numpy as np

from colony.utils.image_manager import ImageManager
from colony.characters.terrain import TerrainManager
from colony.configs.map_generator.ref import BUILDABLE

TECH_CAP: int = 3


@dataclass
class Building:
    """
    Attributes
        id: unique id of building
        type: type of building, like "stroage", "r11"
        tech_level: current level of building
        location: (x, y) location on bitmap
        orientation: used for visualization, determines index of image assets to draw.
    """

    id: int
    type: str
    tech_level: int
    location: Tuple[int, int]
    orientation: Optional[int] = 0


class ColonyBuildingManager:
    """Manages building objects in a colony."""

    def __init__(
        self,
        terrain_man: TerrainManager,
        combined_step: Dict[Tuple[int, int], Any],
        image_manager: ImageManager = None,
        seed: int = 720,
    ):
        self.terrain_man: TerrainManager = terrain_man
        # width and height to calculate random locations
        self.height, self.width = self.terrain_man.bitmap.shape
        # imager to retrive building orientation information
        self.image_manager: ImageManager = image_manager
        # colony spore locations
        self.combined_step: Dict[Tuple[int, int], Any] = combined_step

        # building tracking dictionary
        self.buildings: Dict[int, Building] = {}
        # unique building ids
        self.building_id: int = 0,
        # colony building locations
        self.building_step: Dict[Tuple[int, int], Building] = {}
        # cached available locations; used for randomly getting available tiles.
        #   since avalialbe locations will change overtime, each time a new building was
        #   requested to be built on random locations, this list will be reset
        self.available_tiles: List[Tuple[int, int]] = []
        # rng for random locations, orientations, etc.
        self.rng = np.random.RandomState(seed)

    def update_combined_step(self, combined_step: Dict[Tuple[int, int], Any]):
        """Should be called at the end of each iteration, such that building manager can
        get up-to-date information of current tile info."""
        self.combined_step = combined_step

    def progress_building_step(self):
        pass
        

    def add_building_non_image(self, building_type: int):
        pass

    def get_random_coor_naive(self) -> Tuple[int, int]:
        """Roll a pair of x y to form a random coor."""
        x: int = self.rng.randint(low=0, high=self.width)
        y: int = self.rng.randint(low=0, high=self.height)
        return x, y
    
    def get_random_coor(self, tried: int = -1) -> int:
        """
        Roll a pair of coor from unoccupied tiles.
        We first find all available tiles and cache them into a class variable,
        and then randomly choose one. If that one doesn't work (like 2x1 buildings),
        then in the next iteration we delete that coor ("tried" variable) from
        the set and get another random one. If we tried all of them and none worked,
        then return None to indicate no such tile exists.

        Args
            tried: parsed by caller who is supposed to be a loop trying to enumerate
                all possible tiles. If we parse a coor to it and that didn't work,
                then that coor, or to be more specific, its index should become this 
                "tried" variable such that we can remove it from random selection pool.

        Returns
            int: index of locations saved in cached available tiles.
        """
        # tried is parsed when previous one doesn't work, therefore remove it
        if tried != -1:
            del self.available_tiles[tried]
            # if after removal the set become empty, then there is no such a tile
            # that can fit our building, therefore return None
            if len(self.available_tiles) == 0:
                return -1

        if len(self.available_tiles) == 0:
            # if the available was not calculated (this happens at the first iteration)
            # then we add all empty tiles to cache
            for x in range(self.width):
                for y in range(self.height):
                    coor: Tuple[int, int] = (x, y)
                    if coor not in self.combined_step and \
                        coor not in self.building_step:
                        self.available_tiles.append(coor)
        # return a random index in cache
        return self.rng.choice(len(self.available_tiles))

    ########################
    ### building helpers ###
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

    

    ### building helpers ###
    ########################

    def add_building(
            self,
            type: int,
            loc: Tuple[int, int] = None,
            tech: int = 0,
            orientation: int = None,
        ) -> bool:
        """
        Do checks and build the building if we can.
        1. Physical checks: if given location and orientation will have free tiles;
        2. Resource checks: if storage can support such a building.
        If checks passed, then build it and deduct resources from colony.

        There are cases when location or orientation not specified:
        1. If neither were given, then chose a random location and random orientation.
        2. If only location was given, then check all possible orientations and
            randomly select one.
        3. If only orientation was given, then choose a random location (or keep trying
            until all tiles are exhauseted)
        """
        can_be_built: bool = False
        # check if this building can be added
        # get list of available orientations:
        avail_ori: List[Tuple[int, int]] = self.image_manager.sizes[type]

        # two key variables for building
        buildable_loc: Tuple[int, int] = None
        buildbale_ort: int = -1  # -1 for invalid

        # case 0: when both loc and orientation are given
        if (loc is not None) and (orientation is not None):
            if self.validate_loc_and_ori(loc, avail_ori[orientation]):
                buildable_loc = loc
                buildbale_ort = avail_ori[orientation]
        # case 1: neither were given
        elif loc is None:
            if orientation is None:
                loc_id: int = self.get_random_coor(tried=-1)  # -1 for first iteration
                if loc_id == -1:  # return value -1 means no tiles available
                    return False  # impossible to build because no tiles available

                random_loc: Tuple[int, int] = self.available_tiles[loc_id]
                random_ori: int = self.build_at_location_with_random_orientation(
                    loc=random_loc, sizes=avail_ori
                )
                while random_ori == -1:  # -1: cannot be built on this tile, so try another
                    # parse last loc_id to remove it from cache
                    loc_id = self.get_random_coor(tried=loc_id)
                    if loc_id == -1:  # return value -1 means no tiles available
                        return False  # impossible to build because no tiles available

                    random_loc = self.available_tiles[loc_id]
                    random_ori = self.build_at_location_with_random_orientation(
                        loc=random_loc, sizes=avail_ori
                    )
                buildable_loc = random_loc
                buildbale_ort = random_ori
            # case 3: only orientation was given
            else:
                pass





        # parsed orientation, then check this orientation and location
        if orientation is not None:
            can_be_built = self.validate_loc_and_ori(loc, avail_ori[orientation])

        if loc is None and orientation is None:

            pass
        elif loc is None:
            pass

        if not can_be_built:
            return False

        # if can be built, then add it
        # enumerate building id
        new_building_id: int = self.building_id
        self.building_id += 1

        if self.image_manager is None:
            self.add_building_non_image(building_id=new_building_id)
        if orientation is None:
            orientation = 0

        new_building: Building = Building(
            id=id, type=type, location=loc, tech=tech, orientation=orientation
        )
        self.buildings[id] = new_building
        return False

    def upgrade_building(self, id: int) -> bool:
        """Upgrade an existing building, returns whether it will be successful."""
        if self.buildings[id].tech_level < TECH_CAP:
            self.buildings[id].tech_level += 1
            return True
        return False

    def downgrade_building(self, id: int) -> bool:
        """Downgrade an existing building, returns whether it will be successful."""
        if self.buildings[id].tech_level > 1:
            self.buildings[id].tech_level -= 1
            return True
        return False

    def demolish_building(self, id: int) -> bool:
        """Remove an existing building, returns whether it will be successful."""
        pass
