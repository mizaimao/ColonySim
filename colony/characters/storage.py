from dataclasses import dataclass, field
from abc import ABC
from typing import Dict, Optional


RES_MAPPING: Dict[int, str] = {
    11: "Food",

    21: "Wood",
    22: "Stone",
    23: "Metal"
}


@dataclass
class Storage(ABC):
    res: Dict[int, int] = field(default_factory=lambda: {})


@dataclass
class ColonyStorage(Storage):
    resource_limits: Optional[Dict[int, int]] = field(default_factory=lambda: {
        11: 2000,
        21: 500,
        22: 250,
        23: 250
    })

@dataclass
class SporeStorage(Storage):
    resource_limit: Optional[int] = 10
