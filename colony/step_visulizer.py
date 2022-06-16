from typing import Callable, Dict, Tuple
import cv2
import numpy as np

from configs.map_generator.ref import map_ref
from colony_def import Colony
from population_plotter import PopulationCurve
from configuration import MapSetup, map_cfg, world_cfg, WorldSetup
from scene_painter import ColonyView, ColonyView2D, ColonyViewIso

painters: Dict[str, ColonyView] = {
    "2D": ColonyView2D,
    "isometric": ColonyViewIso,
}

POP_FONT: int = cv2.FONT_HERSHEY_DUPLEX
POP_TEXT_COLOR: Tuple[int, ...] = (100, 100, 100, 0)

# color of players in BGR
color_dict: Dict[int, Tuple[int, ...]] = {1: (245, 158, 66), 3: (95, 95, 250)}


class StepVisulizer:
    """
    Visualize a single step in colony
    """

    def __init__(
        self,
        colony: Colony,
        map_cfg: MapSetup = map_cfg,
        world_cfg: WorldSetup = world_cfg,
    ):
        """
        Args:
            colony {Colony} -- pointer to a colony object saved in memory
            pop_curve {PopulationCurve} -- pointer to a curve plotting object in memory
        """
        # setup painter
        self.colony = colony
        self.bitmap = map_cfg.bitmap
        self.frame_height = colony.viewer_height
        self.frame_width = colony.viewer_width

        painter_class = painters["isometric"]
        # painter_class = painters["2D"]

        self.painter = painter_class(
            self.colony.width,
            self.colony.height,
            self.frame_width,
            self.frame_height,
            self.bitmap,
        )
        self.static_frame = self.painter.get_static_frame()
        self.painter.paint_playground()

        self.multiplier = self.painter.multiplier

        # fixed values
        self.font_scalar = 0.05 * self.multiplier
        self.font_space = int(5 / 3 * self.multiplier)
        self.font_above = int(5 / 3 * self.multiplier)
        self.font_front = int(2 / 3 * self.multiplier)
        # displaying info
        self.info_pane_height = int(self.frame_height * 0.2)
        self.left_info_pane_width = int(self.frame_width / 2)
        self.right_info_pane_width = self.frame_width - self.left_info_pane_width
        # pointers to objects in memory
        self.colony = colony
        self.pop_curve = PopulationCurve(
            width=self.right_info_pane_width, height=self.info_pane_height
        )

    def plot_step(self, cycle: int = -1):
        """
        Plot a step. Info is accessed by the pointer to colony object.
        The plot is made of upper and lower parts:
            upper part contains enlarged representation of current tiles
            lower part contains two panes
                left pane showing current population and cycle number
                right pane showing population curve

        Args:
            cycle {int} -- cycle number that will be displayed on info pane
        """
        frame = self.static_frame.copy()
        # need to sort spores to paint them in a correct order, this is needed for isometrci viewing
        _tempList = sorted(self.colony.step.keys(), key=lambda x: x[0], reverse=True)
        step_sorted = sorted(_tempList, key=lambda x: x[1])

        # upper pane, paint all spores
        for (x, y) in step_sorted:
            spores = self.colony.step[(x, y)]
            # show only the first spore
            top_spore = self.colony.spores[spores[0]]
            # dye this block
            splore_color = color_dict[top_spore.sex]
            self.painter.paint_large_pixel(frame, x, y, splore_color)

        # lower panes
        # left info pane
        left_info = np.full(
            (self.info_pane_height, self.left_info_pane_width, 3), 220, dtype=np.uint8
        )
        cv2.putText(
            left_info,
            "Colony Size: {}".format(self.colony.current_pop),  # size counter
            (self.font_front, self.font_above),  # position
            POP_FONT,
            self.font_scalar,  # font and scale
            POP_TEXT_COLOR,
            3,
        )  # linetype
        cv2.putText(
            left_info,
            "Cycle: {}".format(cycle),  # cycle counter
            (self.font_front, self.font_above + self.font_space),  # pos
            POP_FONT,
            self.font_scalar,
            POP_TEXT_COLOR,
            3,
        )

        # right plot pane, making the curve plot
        right_plot = self.pop_curve.update_and_plot(self.colony.current_pop)

        # put two panes together
        below_addon = np.concatenate([left_info, right_plot], axis=1)
        return np.concatenate([frame, below_addon], axis=0)
