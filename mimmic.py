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

    chicken_col = Colony(width=X, height=Y, init_pop=INIT_POP, seed=0)
    # a is an np array
    a = convert_step_to_array(chicken_col)
    cv2.imshow('image', a) 
    
    k = ord('n')
    while k==ord('n'):
        
        chicken_col.progress_a_step()
        a = convert_step_to_array(chicken_col)
        cv2.imshow('image', a) 
        k = cv2.waitKey(0)
    cv2.destroyAllWindows()
