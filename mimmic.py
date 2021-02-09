#!/usr/bin/env python3

import cv2
import sys
import numpy as np

from colony import Colony
from step_visulizer import *

X = 32
Y = 20

if __name__ == '__main__':
    try:
        x = int(sys.argv[1])
        y = int(sys.argv[2])
    except:
        x = X
        y = Y
    
    k = ord('n')
    while k==ord('n'):
        chicken_col = Colony(width=X, height=Y, init_pop=10, seed=0)
        a = convert_step_to_array(chicken_col)
        cv2.imshow('image', a) # a is an np array
        k = cv2.waitKey(0)
    cv2.destroyAllWindows()
