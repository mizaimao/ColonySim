"""Reference of numbers in map bitmap and definition.
"""
from telnetlib import SE
from typing import Dict, Set, Tuple

STRUCTURE_PREFIX: int = 7
# buildale tiles
BUILDABLE: Set[int] = {101, }
# passiable tiles; tiles not in this set won't allow spores to step on
PASSABLE: Set[int] = {101, 111, 7110, 7210}

# NOTE: color codes are in RGB
map_ref: Dict[int, Tuple] = {
    # normal tile range should be 0-999
    # 0-100 are reserved for moviable objects
    # 4-digits, or thousands are buildings
    # 0-postfixes, virtual building tiles. E.g. a building may occupy
    #   more than 1 tiles, therefore if a farm having code 11 occipies four tiles,
    #   then the start-drawing-point will have code 7111 (level 1), while the other
    #   three will have code 7110 (see the appending 0)
    # 1, 2, 3, 4 postfixes, building code with tech level.
    1: ("blue spore", (245, 158, 66)),
    3: ("red spore", ((95, 95, 250))),

    # 101-200: vege
    101: ("grass", (57, 191, 141)),
    111: ("tree", (66, 105, 47)),

    # 201-300: water
    201: ("water", (0, 105, 148)),

    # 301-500: solids
    301: ("mountain", (122, 115, 114)),

    # 701-799: structures
    7110: ("farm area", (70, 87, 96)),
    7111: ("farm (lv.1)", (70, 87, 96)),
    7112: ("farm (lv.2)", (70, 87, 96)),
    7113: ("farm (lv.3)", (70, 87, 96)),
    7114: ("farm (lv.4)", (70, 87, 96)),

    7210: ("timber area", (24, 56, 101)),
    7211: ("timber (lv.1)", (24, 56, 101)),
    7212: ("timber (lv.2)", (24, 56, 101)),
    7213: ("timber (lv.3)", (24, 56, 101)),
    7214: ("timber (lv.4)", (24, 56, 101)),
}
