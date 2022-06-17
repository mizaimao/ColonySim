"""Small class stores information for print-out.
"""
from typing import Callable, List, Tuple, Union
from dataclasses import dataclass


@dataclass
class InfoManager:
    """Stores and filter information for printing out.
    """
    def __init__(self, silent_mode: bool = False):
        """The idea is to add new information to stack, and by the end of each cycle,
        the info will be printed (if choose to do so) and copied to history stack.
        
        Args
            silent_mode: mute printing (e.g. program runs in frame-dumpping mode)
        """
        self.info_stack: List[str] = []
        self.info_history: List[List[str]] = []

        self.silent_mode: bool = silent_mode

    def merge_stack(self):
        """Push current stack to history.
        """
        self.info_history.append(self.info_stack.copy())
        self.info_stack.clear()


    def print_info(self, force_print: bool = False):
        """Print each info saved in stack by order. This also transfers everything in stack to history.

        Args:
            force_print: overrides silent mode.
        """
        if (not self.silent_mode) or force_print:
            for info_str in self.info_stack:
                print(info_str)
        self.merge_stack()


    def info(self, info_str: str):
        """Add a single string to stack.
        """
        assert info_str
        self.info_stack.append(info_str)
