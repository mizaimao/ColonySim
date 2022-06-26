from dataclasses import dataclass
from typing import Tuple

from colony.characters.storage import SporeStorage

@dataclass
class Spore:
    sid: int
    sex: int
    age: int
    health: int

    storage: SporeStorage
