from typing import Callable, Dict, List, Tuple, Union
import numpy as np

from colony.configs.map_generator.ref import map_ref
from colony.characters.colony import Colony
from colony.vis.curve_painter import CurvePainter
from colony.configuration import MapSetup, map_cfg, world_cfg, WorldSetup
from colony.characters.storage import RES_MAPPING

from colony.vis.main_scene_painter import MainScenePainter
from colony.vis.string_painter import StringPainter, InfoPanePainter, add_info_to_main_pane

INFO_STR_POS: int = 8  # width (number of digits) of info displaying string of resources


class StepVisulizer:
    """
    Visualize a single step in colony. Builds and merges multiple panes to form a unified viewer.
    """

    def __init__(self, colony: Colony, map_cfg: MapSetup = map_cfg):
        """
        Args
            colony: pointer to a colony object saved in memory
            map_cfg: map configuration instance
        """

        self.colony: Colony = colony
        frame_height: int = colony.viewer_height
        frame_width: int = colony.viewer_width
        self.bitmap: np.ndarray = map_cfg.bitmap

        # setup pane sizes
        info_pane_height: int = int(frame_height * 0.2)  # shared by two lower panes
        left_info_pane_width: int = int(frame_width / 2)
        right_info_pane_width: int = frame_width - left_info_pane_width

        painter_style: str = "isometric_image"
        #painter_style: str = "isometric"
        #painter_style = "2D"

        # setup painters (three panes)
        self.main_painter = MainScenePainter(  # main view (upper pane)
            painter_style,
            self.colony,
            self.bitmap,
            frame_width,
            frame_height)
         # colony info painter (lower left pane)
        self.info_pane_painter: InfoPanePainter = InfoPanePainter(
            width=left_info_pane_width,
            height=info_pane_height
            )
        # colony debugging info painter (overlays upper pane)
        self.main_view_string_painter: StringPainter = None
        # pop curve painter
        self.curve_painter = CurvePainter(right_info_pane_width, info_pane_height)

    def paint_main_viewer(self, with_info: bool = False) -> np.ndarray:
        """Paint the colony main viewer, i.e. the dots and playground.
        This mutates the input frame as a result of np.array manipulation.
        """
        frame = self.main_painter.paint_main_scence()

        res11_info = "{}: {:5d}".format(RES_MAPPING[11], int(self.colony.res_man.storage.res[11]))
        res21_info = "{}: {:5d}".format(RES_MAPPING[21], int(self.colony.res_man.storage.res[21]))
        res22_info = "{}: {:5d}".format(RES_MAPPING[22], int(self.colony.res_man.storage.res[22]))
        res23_info = "{}: {:5d}".format(RES_MAPPING[23], int(self.colony.res_man.storage.res[23]))
        self.main_view_string_painter = add_info_to_main_pane(
            self.main_view_string_painter,
            self.colony,
            frame,
            steps=5,
            max_rows=30,
            custom_lines=[
                res11_info,
                res21_info,
                res22_info,
                res23_info,
            ]
        )

        # if with_info:
        #     self.main_view_string_painter = add_info_to_main_pane(self.main_view_string_painter, self.colony, frame, steps=5, max_rows=20)
        return frame

    def paint_info_pane(self) -> np.ndarray:
        """Paint infomation pane, containing items like cycle count and population.
        """
        colony_size_info = "Colony Size: {}/{}".format(
            self.colony.spore_man.current_pop, self.colony.spore_man.pop_cap
        )
        colony_cycle_info = "Iteration: {}".format(self.colony.current_iteration)
        # # add text info to pane
        left_info = self.info_pane_painter.paint_lines([
            colony_size_info,
            colony_cycle_info
        ])
        return left_info

    def plot_step(self):
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
        info_pane: np.ndarray = self.paint_info_pane()

        # right plot pane, making the curve plot
        curve_pane: np.ndarray = self.curve_painter.draw_colony_curves(self.colony)

        # put lower two panes together
        below_addon = np.concatenate([info_pane, curve_pane], axis=1)
        # return concatenated uppwer and lower panes
        return np.concatenate([viewer_pane, below_addon], axis=0)
