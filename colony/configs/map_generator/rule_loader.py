"""Detailed map generation rules.
"""
import yaml
from dataclasses import dataclass
from typing import Dict, Tuple


RULES = "configs/map_generator/rules.yaml"

@dataclass
class GreenMapRules:
    def __init__(self, cfg: dict):
        # mountains
        self.mountain_percentage: float = cfg["mountain_percentage"]

        # water bodies
        self.water_types: Dict[str, float] = cfg["water_types"]
        self.water_percentage: float = cfg["water_percentage"]
        self.water_upper_limit: float = cfg["water_upper_limit"]

        # vegies
        self.wood_percentage: float = cfg["wood_percentage"]


def load_rules(map_type: str):
    """Returns a map rule dataclass object with given map type and config name.
    """
    all_cfg = yaml.load(open(RULES))
    rules = None
    if map_type == "green":
        cfg = all_cfg["GreenMapRules"]
        rules = GreenMapRules(cfg)

    return rules
        