#!/usr/bin/env python3

import cv2
import sys
import numpy as np

from colony import Colony
from step_visulizer import *

X = 32
Y = 20
INIT_POP = 10

if __name__ == '__main__':
    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
    except:
        x = X
        y = Y

    # create a colony
    chicken_col = Colony(width=X, height=Y, init_pop=INIT_POP, seed=0)
    
    # plotting object
    visualizer = StepVisulizer(chicken_col, multiplier=50)
    
    cycle_counter = -1
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
