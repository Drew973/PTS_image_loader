# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 10:41:05 2024

@author: Drew.Bennett
"""
K = 3
S = 0
N = 2
MAX = 99999999999999999999.9


import numpy as np
from scipy import interpolate
from qgis.core import QgsGeometry,QgsPointXY
from scipy.optimize import minimize_scalar

#numpy array. m,x,y
#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5



def leftPerp(vect):
    return np.array([vect[1],-vect[0]])


#[(x,y)] or ()
def to2DArray(x,y):
    return np.array([[x,y]],dtype = float)




class splineString:
    
    def __init__(self):
        self.xSpline = None
        self.ySpline = None
        self.xDerivitive = None
        self.yDerivitive = None


#3 column numpy array. m,x,y
    def setValues(self,values):
       # print('setValues',values)
        if len(values) >= K:
            self.xSpline = interpolate.UnivariateSpline(values[:,0], values[:,1] , s = S, ext='const', k = K)
            self.ySpline = interpolate.UnivariateSpline(values[:,0],  values[:,2] , s = S, ext='const', k = K)
            self.xDerivitive = self.xSpline.derivative(1)
            self.yDerivitive = self.ySpline.derivative(1)    
        else:
            self.xSpline = None
            self.ySpline = None
            self.xDerivitive = None
            self.yDerivitive = None    
    
    #->bool
    def hasPoints(self):
        return self.xSpline is not None
    
    # array[[x,y]] or []
    def point(self,mo):
        if self.hasPoints():
            m = mo[:,0]
            r = np.zeros((len(m),2)) * np.nan
            r[:,0] =  self.xSpline(m)
            r[:,1] = self.ySpline(m)
            offsets = mo[:,1]
          #  if not np.any(offsets):
            perps = self.leftPerp(m)#([x],[y])
            r[:,0] = r[:,0] + perps[:,0] * offsets
            r[:,1] = r[:,1] + perps[:,1] * offsets
            return r
        return []
    

    #convert geometry in terms of m,offset to x,y
    #QgsGeometry
    # x as m. y as offset
    def moGeomToXY(self,geom,mShift = 0.0,offset = 0.0):
        g = QgsGeometry(geom)
        mo = []
        for i,v in enumerate(g.vertices()):
            mo.append([v.x()+mShift,v.y()+offset])
           # p = to2DArray(v.x()+mShift,v.y()+offset)
        mo = np.array(mo)
        new = self.point(mo)
        for i,row in enumerate(new):
            g.moveVertex(row[0],row[1],i)
        return g


    #perpendicular unit vectors at m
    def leftPerp(self,m):
        if self.hasPoints():
            r = np.zeros((len(m),2)) * np.nan
            dx = self.xDerivitive(m)
            dy = self.yDerivitive(m)
            magnitudes = np.sqrt(dx*dx+dy*dy)
            r[:,0] = -dy/magnitudes
            r[:,1] = dx/magnitudes
            return r

    
    #cartestian to 'ribbon' coordinates
    #nearest m,o to point xy
    #could find m more efficiently by solving d distance/dm = 0?
    #numpy uses numeric methods to solve higher order polynomials. might not be faster.
    def locate(self, point:QgsPointXY , minM:float = 0.0 , maxM:float = np.inf , maxOffset:float = 20.0 , tol:float = 0.01): #-> Tuple(float,float)  
        if not self.hasPoints():
            raise ValueError('No points loaded.')
    
        def _dist(m):
            mo = np.array([[m,0]])
         #   print('mo',mo)
            p = self.point(mo)
         #   print('p',p)
            if len(p)>0:
                pt = QgsPointXY(p[0,0],p[0,1])
                return pt.distance(point)
           # print('dist',pt.distance(point))
            return MAX
        
        res = minimize_scalar(_dist,bounds = (minM,maxM),method='bounded',tol = tol)
        
        if res.success:
            m = res.x
            #distance = res.fun#distance
            
            nearest = self.point(np.array([[m,0]]))
            shortestLine = nearest[0] - np.array([point.x(),point.y()])
            perp = self.leftPerp([m])[0]
            offset = -np.dot(perp,shortestLine)
            if abs(offset) > maxOffset:
                raise ValueError('Nearest point outside maximum offset.')
            
            return (m,offset)
        else:
            raise ValueError('Could not minimize distance')


if __name__ == '__console__':
    s = splineString()
    vals = np.array([[0,10,20,30,40],[0,5,10,15,20],[0,0,0,0,0]],dtype = float).transpose()
   # print('vals',vals)
    s.setValues(vals)
    
    p = QgsPointXY(10,10)
    r = s.locate(p,0,100)
    print(r)
