# -*- coding: utf-8 -*-
"""
similar to linestringM but models line as smooth curve through known points.
smooth curve has well defined direction for every chainage. 
need continous 1st derivitives.
quadratic spine has this.
"""
K = 2
#K = 3
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
    
    #3 column numpy array. m,x,y

    def __init__(self,values):
        self.xSpline = interpolate.UnivariateSpline(values[:,0], values[:,1] , s = S, ext='const', k = K)
        self.ySpline = interpolate.UnivariateSpline(values[:,0],  values[:,2] , s = S, ext='const', k = K)
        self.xDerivitive = self.xSpline.derivative(1)
        self.yDerivitive = self.ySpline.derivative(1)    

    
    # array[[x,y]] or []
    # m in any units.
    #offset in same units as x and y.
    def point(self,mo):
          m = mo[:,0]
          r = np.zeros((len(m),2)) * np.nan
          r[:,0] =  self.xSpline(m)
          r[:,1] = self.ySpline(m)
          offsets = mo[:,1]
          perps = self.leftPerp(m)#([x],[y])
          r[:,0] = r[:,0] + perps[:,0] * offsets
          r[:,1] = r[:,1] + perps[:,1] * offsets
          return r
    
    #array of m values
    #array [(x1,y1),(x2,y2)...]
    def centerLinePoint(self,m):
        return np.column_stack([self.xSpline(m) , self.ySpline(m)])
    

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
        r = np.zeros((len(m),2)) * np.nan
        dx = self.xDerivitive(m)
        dy = self.yDerivitive(m)
        magnitudes = np.sqrt(dx*dx+dy*dy)
        r[:,0] = -dy/magnitudes
        r[:,1] = dx/magnitudes
        return r


    def nearestM(self , x : float , y : float , minM:float = 0.0 , maxM:float = np.inf , tol:float = 0.01) -> float:
        def _sqdist(m):
            p = self.centerLinePoint(m)# like p [[ 495866.03275013 4198850.1469678 ]]
            return (p[0,0] - x) * (p[0,0] - x) + (p[0,1] - y) * (p[0,1] - y)
        
        res = minimize_scalar(_sqdist,bounds = (minM,maxM),method='bounded',tol = tol)
        if res.success:
            return res.x            
        else:
            raise ValueError('Could not minimize distance')


    
    #cartestian to 'ribbon' coordinates
    #nearest m,offset to point xy
    #could find m more efficiently by solving d distance/dm = 0?
    #numpy uses numeric methods to solve higher order polynomials. might not be faster.
    def locate(self, x : float , y : float , minM:float = 0.0 , maxM:float = np.inf , tol:float = 0.01): #-> Tuple(float,float)
        m = self.nearestM(x = x, y = y ,minM = minM , maxM = maxM , tol = tol)
        nearest = self.centerLinePoint(m)#like [[ 494899.23345296 4197063.37078011]]
        shortestLine = nearest[0] - np.array([x,y])
        perp = self.leftPerp([m])[0]
        offset = -np.dot(perp,shortestLine)
        return (m,offset)
      

        


if __name__ == '__console__':
    s = splineString()
    vals = np.array([[0,10,20,30,40],[0,5,10,15,20],[0,0,0,0,0]],dtype = float).transpose()
   # print('vals',vals)
    s.setValues(vals)
    
    p = QgsPointXY(10,10)
    r = s.locate(p,0,100)
    print(r)
