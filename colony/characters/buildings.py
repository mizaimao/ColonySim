"""Building objects for colony."""
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

TECH_CAP: int = 3

@dataclass
class Building:
    """
    Attributes
        id: unique id of building
        type: type of building, like "stroage", "r11"
        tech_level: current level of building
        location: (x, y) location on bitmap
        orientation: used for visualization, determines index of image assets to draw.
    """
    id: int
    type: str
    tech_level: int
    location: Tuple[int, int]
    orientation: Optional[int] = 0


class ColonyBuildingManager:
    """Manages building objects in a colony."""
    def __init__(self):
        self.buildings: Dict[int, Building] = {}
        
    def add_building(
        self,
        id: int, 
        type: str, 
        loc: Tuple[int, int], tech: int = 0, orientation: int = None):

        if orientation is None:
            orientation = 0

        new_building: Building = Building(
            id=id,
            type=type,
            location=loc,
            tech=tech,
            orientation=orientation
        )
        self.buildings[id] = new_building

    def upgrade_building(self, id: int) -> bool:
        """Upgrade an existing building, returns whether it will be successful.
        """
        if self.buildings[id].tech_level < TECH_CAP:
            self.buildings[id].tech_level += 1
            return True
        return False

    def downgrade_building(self, id: int) -> bool:
        """Downgrade an existing building, returns whether it will be successful.
        """
        if self.buildings[id].tech_level > 1:
            self.buildings[id].tech_level -= 1
            return True
        return False

    def demolish_building(self, id: int) -> bool:
        """Remove an existing building, returns whether it will be successful.
        """
        pass
