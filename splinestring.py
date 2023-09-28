# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:52:57 2023

@author: Drew.Bennett


linestringM with cubic spline. 

1 point: 1 m+offset since derivitive is continuous


"""

from scipy import interpolate
from scipy.optimize import minimize_scalar

import numpy

#numpy array. m,x,y
#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5



def leftPerp(vect):
    return numpy.array([vect[1],-vect[0]])


class points:
    def __init__(self,m,x,y):
        self.m = numpy.array([mVal for mVal in m])
        self.x = numpy.array([xVal for xVal in x])
        self.y = numpy.array([yVal for yVal in y])
        


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
    
    
    def interpolatePoints(self,m,leftOffsets=None):
        x = self.xSpline(m)
        y = self.ySpline(m)
        if leftOffsets is not None:
            perps = self.leftPerps(m)#([x],[y])
            x = x + perps[0] * leftOffsets
            y = y + perps[1] * leftOffsets
        return numpy.stack((x, y))
    

    def rechainage(self,interval):
        if self.m is not None:
            last = None
            length = 0.0
            mVals = []
            for i,m in enumerate(self.m):
                if last is None:
                    last = m
                else:
                    length += self.length(m,last,50)
                    last = m
                mVals.append(length)
        self.setPoints(points(mVals,self.x,self.y))
        
        
    #length between m1 and m2. 
    #n = number of points
    def length(self,m1,m2,n):
        m = numpy.linspace(m1,m2,n,dtype=numpy.double)
        dx = numpy.diff(self.xSpline(m))
        dy = numpy.diff(self.ySpline(m))
        return numpy.sum(numpy.sqrt(dx*dx+dy*dy))
       
        
    #perpendicular unit vectors at m
    def leftPerps(self,m):
        dx = self.xDerivitive(m)
        dy = self.yDerivitive(m)
        magnitudes = numpy.sqrt(dx*dx+dy*dy)
        return numpy.stack([-dy/magnitudes,dx/magnitudes])#[[x],[y]]
    
    
    def leftPerp(self,m):
        p = self.leftPerps(m)
        return numpy.array([p[0,0],p[0,1]])
    
    
    
    def residual(self,points,mShift):
        newM = points.m + mShift
        dx = self.xSpline(newM) - points.x
        dy = self.ySpline(newM) - points.y
        return numpy.sum(dx*dx+dy*dy)+0.05*mShift*mShift#small factor so converges at lowest shift        
        
        
    #return m shift that minimizes distance to points
    def bestMShift(self,points,mVals=None):
        def res(mShift):
            return self.residual(points,mShift)
        
        if mVals is None:
            d = numpy.max(self.m)-numpy.min(self.m)
            return minimize_scalar(res,bounds=(-d, d), method='bounded').x
   
    
    
    def addMShift(self,mShift):
        self.setPoints(points(self.m+mShift,self.x,self.y))
        