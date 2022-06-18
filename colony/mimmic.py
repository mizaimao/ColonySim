#!/usr/bin/env python3
from dataclasses import dataclass
import json
import cv2
import sys
import os
import tqdm

from colony.characters.colony import Colony
from colony.vis.step_visulizer import StepVisulizer
from colony.configuration import world_cfg


target_folder = "/Users/frank/Projects/ColonySim/frames"
target_frame = 24 * 80

# auto progression frames per second
auto_fps = 5


WINDOW_NAME = str(world_cfg.setting_id)
X = world_cfg.width
Y = world_cfg.height
VX = world_cfg.viewer_width
VY = world_cfg.viewer_height
INIT_POP = world_cfg.initial_population


if __name__ == '__main__':
    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
    except:
        x = X
        y = Y

    mode = 'interactive'
    #mode = 'dump'
    #mode = 'autoplay'

    # create a colony
    chicken_col = Colony(
        width=X,
        height=Y,
        viewer_width=VX,
        viewer_height=VY,
        init_pop=INIT_POP,
        seed=0,
        verbose=(mode!='dump'))
    # plotting object
    visualizer = StepVisulizer(colony=chicken_col)
    
    cycle_counter = -1
    single_frame = visualizer.plot_step() # returns an np.array

    # manual progression by pressing a key
    if mode == "interactive":        
        k = ord('n')
        while k==ord('n'):
            cycle_counter += 1
            
            colony_survived: bool = chicken_col.progress_a_step()
            chicken_col.printer.print_info()
            single_frame = visualizer.plot_step()
            cv2.imshow(WINDOW_NAME, single_frame)
            k = cv2.waitKey(0)
            if not colony_survived:
                break
        cv2.destroyAllWindows()

    # generate each step as a frame and save these images
    elif mode == "dump":
        frame = 0
        for frame in tqdm.tqdm(range(target_frame)):
            cycle_counter += 1        
            colony_survived = chicken_col.progress_a_step()
            chicken_col.printer.print_info()
            single_frame = visualizer.plot_step()

            out_name = os.path.join(target_folder, '%05d.png' % frame)
            cv2.imwrite(out_name, single_frame)
            if not colony_survived:
                break
        print("Frames generated, converting it to video...")
        # ffmpeg -r 24 -i %05d.png -vcodec mpeg4 -y colony.mp4
        #os.system(f"ffmpeg -r 24 -i {target_folder}/%05d.png -vcodec mpeg4 -y colony.mp4")

    # auto progression
    elif mode == "autoplay":
        interval = int(1 / auto_fps * 1000)
        while True:
            cycle_counter += 1
            
            colony_survived = chicken_col.progress_a_step()
            chicken_col.printer.print_info()
            single_frame = visualizer.plot_step()
            cv2.imshow(WINDOW_NAME, single_frame)
            key = cv2.waitKey(interval)  # this one controlls time interval
            if key > 0:
                cv2.destroyAllWindows()
                break
            if not colony_survived:
                break
    else:
        raise NotImplementedError()
