"""Holding multiple types of settings for importing.
"""
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Any

from colony.generators.map_generator import GreenMapGenerator

config_path = Path(__file__).parent.joinpath("configs")
map_generator_mapper: dict[str, Any] = {"green": GreenMapGenerator}


@dataclass
class SporeSettings:
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

    one_night_chance: float
    fertility_rate: float
    duel_fatality: float
    natural_fatality: float
    crowd_threshold: int


# objected shared in multiple places
spore_cfg = SporeSettings(
    **json.load(open(config_path.joinpath("spore_beheavoir/default.json"), "r"))
)


@dataclass
class WorldSetup:
    """Some general settings for world."""

    setting_id: str
    width: int
    height: int
    initial_population: int
    viewer_width: int
    viewer_height: int


world_cfg = WorldSetup(**json.load(open(config_path.joinpath("world/default.json"), "r")))


@dataclass
class MapSetup:
    """Map settings and pointers to generators and bitmaps."""

    def __init__(
        self,
        config: dict,
        world_cfg: WorldSetup,
        seed: int = 19930720,
    ):
        """
        Args
            seed: seed for each types of generator.
            world_cfg: pointer to world configs to access info like map size.
        """
        assert isinstance(seed, int)
        self.seed = seed

        self.map_description: str = config["map_description"]
        self.map_type: str = config["map_type"]

        map_generator_class = map_generator_mapper[self.map_type]
        map_generator = map_generator_class(
            self.seed, width=world_cfg.width, height=world_cfg.height
        )
        self.bitmap = map_generator.get_bitmap()


map_cfg = MapSetup(
    json.load(open(config_path.joinpath("map_generator/default.json"), "r")), world_cfg
)
