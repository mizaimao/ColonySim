"""Reference of numbers in map bitmap and definition.
"""
from typing import Tuple

map_ref: dict[int, Tuple] = {
    # 0-100 reserved for moviable objects

    # 101-200: vege
    101: ("grass", (52, 140, 49)),
    111: ("tree", (66, 105, 47)),

    # 201-300: water
    201: ("water", (0, 105, 148)),

    # 301-500: solids
    301: ("mountain", (122, 115, 114)),

}
