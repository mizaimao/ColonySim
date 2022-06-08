"""All types of map generators are defined here.
"""
import abc
import re
import numpy as np
from configs.map_generator.rule_loader import GreenMapRules, load_rules
from .map_element_gen.water_generator import add_single_waterbody


class GreenMapGenerator():
    """Generator for grass-based map.
    """
    def __init__(self, seed: int = None, width: int = None, height: int = None):
        """
        Args
            seed: seed for this generator.
            world_cfg: use this pointer to access world infomration like size.

        """
        self.rng = np.random.RandomState(seed)

        # map place holder
        self.map = np.full(shape=(width, height), fill_value=101)
        # load map rules
        self.rules = load_rules("green")

        # build the map by the rules
        self._build_map()

    def _build_map(self):
        """Build map by multiple steps with given rules.
        """
        # add water bodies
        self._add_waters()

        # add vegies
        self._add_vegies()

        # add solids
        self._add_solids()

    def _add_waters(self):
        """Add water bodies to the map. First roll what types of water to add and then add them.
        """
        # roll water types with pre-defined possibilities of each type
        water_types, water_type_p = zip(*self.rules.water_types.items())
        assert sum(water_type_p) == 1.0, "Wrong water type percentages, sum inequal to 1"
        water_type = self.rng.choice(water_types, p=water_type_p)

        # acquire water body size for each water body
        water_size = self.rules.water_percentage

        # list of water bodies to add
        waters_to_add = [water_type]
        reroll = 0

        # if rolled a "multiple", then keep rolling
        if water_type == "multiple":
            waters_to_add.pop()
            reroll += 2

        while reroll and \
            (water_size) * len(waters_to_add) <= self.rules.water_upper_limit:  # only if there is not too much water

            water_type = self.rng.choice(water_types, p=water_type_p)
            if water_type == "multiple":
                reroll += 1
            else:
                waters_to_add.append(water_type)
                reroll -= 1

        # add those rolled water bodies one by one
        for water in waters_to_add:
            print(f'water {water} rolled')
            add_single_waterbody(water, int(water_size * self.map.size), self.map, self.rng)  # water size in mega pixel

    def _add_vegies(self):
        return
    
    def _add_solids(self):
        return

    def get_bitmap(self):
        """Return the bitmap of generated map.
        """
        return self.map
