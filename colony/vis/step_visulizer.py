from typing import Callable, Dict, List, Tuple, Union
import numpy as np

from colony.configs.map_generator.ref import map_ref
from colony.characters.colony import Colony
from colony.vis.curve_painter import CurvePainter
from colony.configuration import MapSetup, map_cfg, world_cfg, WorldSetup

from colony.vis.main_scene_painter import MainScenePainter
from colony.vis.string_painter import StringPainter, add_info_to_main_pane


class StepVisulizer:
    """
    Visualize a single step in colony. Builds and merges multiple panes to form a unified viewer.
    """

    def __init__(
        self,
        colony: Colony,
        map_cfg: MapSetup = map_cfg,
    ):
        """
        Args
            colony: pointer to a colony object saved in memory
            map_cfg: map configuration instance
        """

        self.colony: Colony = colony
        self.frame_height: int = colony.viewer_height
        self.frame_width: int = colony.viewer_width
        self.bitmap: np.ndarray = map_cfg.bitmap

        # setup pane sizes
        self.info_pane_height: int = int(self.frame_height * 0.2)  # shared by two lower panes
        self.left_info_pane_width: int = int(self.frame_width / 2)
        self.right_info_pane_width: int = self.frame_width - self.left_info_pane_width

        painter_style: str = "isometric"
        #painter_style = "2D"

        # setup painters (three panes)
        self.main_painter = MainScenePainter(  # main view (upper pane)
            painter_style,
            self.colony,
            self.bitmap,
            self.frame_width,
            self.frame_height)
         # colony info painter (lower left pane)
        self.string_painter: StringPainter = StringPainter()
        # colony debugging info painter (overlays upper pane)
        self.main_view_string_painter: StringPainter = None
        # pop curve painter
        self.curve_painter = CurvePainter(self.right_info_pane_width, self.info_pane_height)

    def paint_main_viewer(self, with_info: bool = False) -> np.ndarray:
        """Paint the colony main viewer, i.e. the dots and playground.
        This mutates the input frame as a result of np.array manipulation.
        """
        frame = self.main_painter.paint_main_scence()
        if with_info:
            self.main_view_string_painter = add_info_to_main_pane(self.main_view_string_painter, self.colony, frame, steps=5, max_rows=20)
        return frame

    def paint_info_pane(self, cycle: int) -> np.ndarray:
        """Paint infomation pane, containing items like cycle count and population.
        """
        left_info: np.ndarray = np.full(
            (self.info_pane_height, self.left_info_pane_width, 3), 220, dtype=np.uint8
        )
        # build text info
        colony_size_info = "Colony Size: {}".format(self.colony.current_pop)
        colony_cycle_info = "Cycle: {}".format(cycle)
        # add text info to pane
        self.string_painter.paint_lines(left_info, [colony_size_info, colony_cycle_info])

        return left_info

    def plot_step(self, cycle: int = -1):
        """
        Plot a step. Info is accessed by the pointer to colony object.
        The plot is made of upper and lower parts:
            upper part contains enlarged representation of current tiles
            lower part contains two panes
                left pane showing current population and cycle number
                right pane showing population curve

        Args:
            cycle: cycle number that will be displayed on info pane
        """        
        # paint viewer pane (upper pane)
        viewer_pane: np.ndarray = self.paint_main_viewer(with_info=False)  # with_info enables on-screen print

        # paint lower panes
        # left info pane
        info_pane: np.ndarray = self.paint_info_pane(cycle)

        # right plot pane, making the curve plot
        curve_pane: np.ndarray = self.curve_painter.draw_colony_curves(self.colony)

        # put two panes together
        below_addon = np.concatenate([info_pane, curve_pane], axis=1)
        return np.concatenate([viewer_pane, below_addon], axis=0)
