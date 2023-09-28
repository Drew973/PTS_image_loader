# -*- coding: utf-8 -*-
"""
Created on Wed Sep 20 10:33:58 2023

@author: Drew.Bennett
"""

import splinestring


def testMShift():
    points = [(0,0,0),(5,5,5),(100,100,100),(1000,1000,1000)]
    g = splinestring.splineStringM(points)
    otherPoints = [(100,0,0),(1200,1100,1100)]
    
   # otherPoints = [(100,100,102)]

    print(g.bestMShift(otherPoints))
    
    
def testPerps():
    points = [(0,0,0),(5,5,5),(100,100,100),(1000,1000,1000)]
    g = splinestring.splineStringM(points)
    print(g.leftPerps([10,20,30,40]))
    
    
if __name__ in ('__console__','__main__'):
    testPerps()