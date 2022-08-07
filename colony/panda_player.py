#!/usr/bin/env python3
import os
import sys
import tqdm

from colony.characters.colony import Colony
from colony.utils.image_manager import ImageManager
from colony.vis.step_visulizer import StepVisulizer
from colony.configuration import world_cfg, res_cfg
from colony.vis.panda.panda_viewer import PandaViewer

# auto progression frames per second
auto_speed: int = 10
FAST_FORWARD: int = 10


WINDOW_NAME = str(world_cfg.setting_id)
X = world_cfg.width
Y = world_cfg.height
VX = world_cfg.viewer_width
VY = world_cfg.viewer_height
INIT_POP = world_cfg.initial_population


DEFAULT_TILE_SET: str = "space"

SEED: int = 720


if __name__ == '__main__':

    mode = 'autoplay'

    # create image manager (image assets related)
    image_manager: ImageManager = ImageManager(
        set_name=DEFAULT_TILE_SET,
        seed=SEED,
    )

    # create a colony
    chicken_col = Colony(
        viewer_width=VX,
        viewer_height=VY,
        init_pop=INIT_POP,
        image_manager=image_manager,
        seed=SEED,
        verbose=(mode!='dump'))

    cycle_counter = -1

    if FAST_FORWARD > 0:
        for _ in tqdm.tqdm(range(FAST_FORWARD), desc="Fast-forwarding..."):
            chicken_col.progress_a_step()
    # plotting object
    #visualizer = StepVisulizer(colony=chicken_col, painter_style=PAINTER_STYLE, image_manager=image_manager)
    panda_viewer: PandaViewer = PandaViewer(colony=chicken_col)

    panda_viewer.run()
