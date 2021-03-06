#!/usr/bin/env python3
import cv2
import sys
import os
import time
import numpy as np

from colony import Colony
from step_visulizer import *

WINDOW_NAME = "Colony Sim"
X = 32
Y = 20
INIT_POP = 10
target_folder = "/home/frank/Projects/ColonySim/frames"
target_frame = 24 * 80
auto_fps = 10

if __name__ == '__main__':
    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
    except:
        x = X
        y = Y

    mode = 'interactive'
    #mode = 'dump'
    mode = 'autoplay'

    # create a colony
    chicken_col = Colony(width=X, height=Y, init_pop=INIT_POP, seed=0)
    # plotting object
    visualizer = StepVisulizer(chicken_col, multiplier=45)
    
    cycle_counter = -1
    single_frame = visualizer.plot_step(cycle=cycle_counter) # returns an np.array

    if mode == "interactive":        
        k = ord('n')
        while k==ord('n'):
            cycle_counter += 1
            
            chicken_col.progress_a_step()
            single_frame = visualizer.plot_step(cycle=cycle_counter)
            cv2.imshow(WINDOW_NAME, single_frame) 
            k = cv2.waitKey(0)
        cv2.destroyAllWindows()

    elif mode == "dump":
        frame = 0
        while frame < target_frame:
            cycle_counter += 1
            frame += 1
            
            chicken_col.progress_a_step()
            single_frame = visualizer.plot_step(cycle=cycle_counter)

            out_name = os.path.join(target_folder, '%05d.png' % frame)
            cv2.imwrite(out_name, single_frame)

        #os.system("ffmpeg -r 24 -i %05d.png -vcodec mpeg4 -y colony.mp4")
    elif mode == "autoplay":
        interval = int(1 / auto_fps * 1000)
        while True:
            cycle_counter += 1
            
            chicken_col.progress_a_step()
            single_frame = visualizer.plot_step(cycle=cycle_counter)
            cv2.imshow(WINDOW_NAME, single_frame) 
            key = cv2.waitKey(interval)
            if key > 0:
                cv2.destroyAllWindows()
                break
    else:
        raise NotImplementedError()