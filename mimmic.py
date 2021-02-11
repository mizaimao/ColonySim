#!/usr/bin/env python3

import cv2
import sys
import numpy as np

from colony import Colony
from step_visulizer import *
from population_plotter import PopulationCurve

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

    chicken_col = Colony(width=X, height=Y, init_pop=INIT_POP, seed=0)
    # obj for plotting pop curve
    pop_curve = PopulationCurve()
    cycle_counter = -1
    # a is an np array
    a = convert_step_to_array(chicken_col, cycle=cycle_counter, pop_curve=pop_curve)
    cv2.imshow('image', a) 
    
    k = ord('n')
    while k==ord('n'):
        cycle_counter += 1
        
        chicken_col.progress_a_step()
        a = convert_step_to_array(chicken_col, cycle=cycle_counter, pop_curve=pop_curve)
        cv2.imshow('image', a) 
        k = cv2.waitKey(0)
    cv2.destroyAllWindows()
