# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:52:57 2023

@author: Drew.Bennett


linestringM with cubic spline. 

1 point: 1 m+offset since derivitive is continuous


"""

from scipy import interpolate
import numpy

#numpy array. m,x,y
#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5



def leftPerp(vect):
    return numpy.array([vect[1],-vect[0]])


class splineStringM:
    
    
    def __init__(self,points):
        self.m = []
        self.x = []
        self.y = []
        for p in points:
            self.m.append(p[0])
            self.x.append(p[1])
            self.y.append(p[2])
         
    
        self.xSpline = interpolate.UnivariateSpline(self.m, self.x , s = 0, ext=2)
        self.ySpline = interpolate.UnivariateSpline(self.m, self.y , s = 0, ext=2)
        self.xDerivitive = self.xSpline.derivative(1)
        self.yDerivitive = self.ySpline.derivative(1)

    
    def interpolatePoint(self,m,leftOffset = 0):
      
        xy = numpy.array([self.xSpline(m),self.ySpline(m)])
    
        if leftOffset == 0:
            return xy
    
        perp = self.leftPerp(m)
    
        return xy + perp*leftOffset
  
    
    def gradient(self,m):
        return self.yDerivitive(m)/self.xDerivitive(m)
  
    
    def tangent(self,m):
        
        y = self.yDerivitive(m)
        x = self.xDerivitive(m)
        
        if y == 0:
            if x>0:
                return numpy.array([1,0])
            if x<0:
                return numpy.array([-1,0])
            
        if x == 0:
            if y>0:
                return numpy.array([0,1])
            if y<0:
                return numpy.array([0,-1])           
            
        return unitVector(numpy.array([1,y/x]))
    
    
    
    
    #perpendicular unit vector. left hand side.
    def leftPerp(self,m):
        return leftPerp(self.tangent(m))
    #[-dy/dx,1]
