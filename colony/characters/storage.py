from dataclasses import dataclass, field
from abc import ABC
from typing import Dict


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
    pass
