"""Holding multiple types of settings for importing.
"""
import json
from dataclasses import dataclass
from typing import Any
from generators.map_generator import GreenMapGenerator

map_generator_mapper: dict[str, Any] = {"green": GreenMapGenerator}


@dataclass
class SporeSettings:
    def __init__(self, config: dict):
        """
        Configuration class
        
        Attributes:
            one_night_chance {float, inclusively between 0 and 1} -- chance of 
                mating when two opposite sex meet
            fertility_rate {float, non-negative)} -- currently not implemented 
            duel_fatality {floate, inclusively between 0 and 1} --
                chance of death when two spores are meet with the same gender
            natural_fatality {floate, inclusively between 0 and 1} -- 
                currently not implemented
            crowd_threshold {int} -- max number of individuals on the same
                tile, above which famine is induced killing all spores on tile
        """
        self.one_night_chance = config["one_night_chance"]
        self.fertility_rate = config["fertility_rate"]
        self.duel_fatality = config["duel_fatality"]
        self.natural_fatality = config["duel_fatality"]
        self.crowd_threshold = config["crowd_threshold"] 

# objected shared in multiple places
spore_cfg = SporeSettings(json.load(open('configs/spore_beheavoir/default.json', 'r')))


@dataclass
class WorldSetup:
    """Some general settings for world.
    """
    setting_id: str = "FAILSAFE SETTINGS"
    width: int = 32
    height: int = 20
    initial_population: int = 10

world_cfg =  WorldSetup(json.load(open('configs/world/default.json', 'r')))


@dataclass
class MapSetup:
    """Map settings and pointers to generators and bitmaps.
    """
    map_description: str = "Failsafe map settings"
    map_type: str = "green"
    
    def __init__(self, seed: int = 19930720, world_cfg: WorldSetup = WorldSetup()):
        """
        Args
            seed: seed for each types of generator.
            world_cfg: pointer to world configs to access info like map size.
        """
        assert isinstance(seed, int)
        self.seed = seed

        map_generator_class = map_generator_mapper[self.map_type]
        map_generator = map_generator_class(self.seed)
        self.bitmap = map_generator.get_bitmap()
