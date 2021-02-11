#!/usr/bin/env python3
import cv2
import sys
import os
import numpy as np

from colony import Colony
from step_visulizer import *

X = 32
Y = 20
INIT_POP = 10
target_folder = "/home/frank/Projects/ColonySim/frames"
target_frame = 24 * 80

if __name__ == '__main__':
    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
    except:
        x = X
        y = Y

    mode = 'interactive'
    #mode = 'dump'

    # create a colony
    chicken_col = Colony(width=X, height=Y, init_pop=INIT_POP, seed=0)
    # plotting object
    visualizer = StepVisulizer(chicken_col, multiplier=45)
    
    cycle_counter = -1

    if mode == "interactive":
        a = visualizer.plot_step(cycle=cycle_counter) # returns an np.array
        cv2.imshow('image', a) 
        
        k = ord('n')
        while k==ord('n'):
            cycle_counter += 1
            
            chicken_col.progress_a_step()
            a = visualizer.plot_step(cycle=cycle_counter)
            cv2.imshow('image', a) 
            k = cv2.waitKey(0)
        cv2.destroyAllWindows()

    elif mode == "dump":
        a = visualizer.plot_step(cycle=cycle_counter) # returns an np.array

        frame = 0
        while frame < target_frame:
            cycle_counter += 1
            frame += 1
            
            chicken_col.progress_a_step()
            a = visualizer.plot_step(cycle=cycle_counter)

            out_name = os.path.join(target_folder, '%05d.png' % frame)
            cv2.imwrite(out_name, a)

        #os.system("ffmpeg -r 24 -i %05d.png -vcodec mpeg4 -y colony.mp4")

    else:
        raise NotImplementedError()