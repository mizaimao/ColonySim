"""Input interface to Colony instances.
"""
import cv2
from typing import Dict, List, Tuple

from colony.characters.colony import Colony


class ColonyCommander:
    """Interface to issue commands to a Colony instance. Many of functions are wrappers to existing
    functions that reside in different sub-modules of the colony instance."""
    def __init__(self, colony: Colony):
        self.colony: Colony = Colony

    def build_structure(self, structure_type: int, level: int, location: Tuple[int, int] = None, orientation: int = None):
        """Add structure to bitmap.

        Args
            structure_type: structure code, each code represents a type of sctructure.
            level: level of structure to build.
            location: location to build. If not supplied, a random location will be used.
            orientation: orientation of the sctructure. If not supplied, use random.
        """
        pass

