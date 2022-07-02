"""Reference of numbers in map bitmap and definition.
"""
from telnetlib import SE
from typing import Dict, Set, Tuple

# buildale tiles
BUILDABLE: Set[int] = {101, }
# passiable tiles
PASSABLE: Set[int] = {101, }

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
    
    # 101-200: vege
    101: ("grass", (57, 191, 141)),
    111: ("tree", (66, 105, 47)),

    # 201-300: water
    201: ("water", (0, 105, 148)),

    # 301-500: solids
    301: ("mountain", (122, 115, 114)),

    # 701-799: structures
    7110: ("farm area", (255, 255, 255)),
    7111: ("farm (lv.1)", (255, 255, 255)),
    7112: ("farm (lv.2)", (255, 255, 255)),
    7113: ("farm (lv.3)", (255, 255, 255)),
    7114: ("farm (lv.4)", (255, 255, 255)),

}
