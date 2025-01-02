# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 14:33:23 2024

@author: Drew.Bennett
"""

import numpy as np
from image_loader.backend import getPoints , getSplineString , downloadGpsLayer
from image_loader.test import profileFunction , profileFolder
import os
import cProfile



def testGetPoints():
    a = getPoints(27700)
    m = a[:,0]
    print('m',m[0:10])
    diff = np.diff(m)
    isIncreasing = np.all(diff > 0)
    print(isIncreasing)
    w = np.where(diff < 0 )
    print('w',w)
  
    
def testGetSplineString():
    profileFile = os.path.join(profileFolder,'getSplineString.prof')
    pr = cProfile.Profile()
    pr.enable()
    s = getSplineString(srid = 27700)
    pr.disable()
    pr.dump_stats(profileFile)
    


    


if __name__ == '__console__':
    testGetPoints()
    testGetSplineString()
    #testLoadLayer()