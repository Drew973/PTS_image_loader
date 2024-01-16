# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:52:57 2023

@author: Drew.Bennett


linestringM with cubic spline. 

1 point: 1 m+offset since derivitive is continuous


"""

from scipy import interpolate
from scipy.optimize import minimize_scalar

import numpy as np

#numpy array. m,x,y
#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5



def leftPerp(vect):
    return np.array([vect[1],-vect[0]])


class points:
    def __init__(self,m,x,y):
        self.x = np.array([xVal for xVal in x])
        self.y = np.array([yVal for yVal in y])
        


class splineStringM:
    
    
    def __init__(self,points):
        self.setPoints(points)

    
    def setPoints(self,points):
        self.m = points.m
        self.x = points.x
        self.y = points.y
        self.xSpline = interpolate.UnivariateSpline(self.m, self.x , s = 0, ext='const')
        self.ySpline = interpolate.UnivariateSpline(self.m, self.y , s = 0, ext='const')
        self.xDerivitive = self.xSpline.derivative(1)
        self.yDerivitive = self.ySpline.derivative(1)    
    
    
    def point(self,mo):
        m = mo[:0]
        x = self.xSpline(m)
        y = self.ySpline(m)
        offsets = mo[:1]
        if not np.any(offsets):
            perps = self.leftPerps(m)#([x],[y])
            x = x + perps[0] * offsets
            y = y + perps[1] * offsets
        return np.stack((x, y))
    
       
        
    #perpendicular unit vectors at m
    def leftPerp(self,m):
        dx = self.xDerivitive(m)
        dy = self.yDerivitive(m)
        magnitudes = np.sqrt(dx*dx+dy*dy)
        return np.stack([-dy/magnitudes,dx/magnitudes])#[[x],[y]]
    
  