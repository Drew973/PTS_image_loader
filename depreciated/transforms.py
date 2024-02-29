# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 09:00:54 2023

@author: Drew.Bennett
"""

import numpy as np
import math
from qgis.core import QgsPointXY



class affine:

    def __init__(self,a=1,b=0,c=0,d=0,e=1,f=0):
        self.m = np.array([[a,b,c],[d,e,f],[0,0,1]],dtype = np.float)
        self.inv = np.linalg.inv(self.m)
        #print('inv',self.inv)
        
    #QgsPointXY->QgsPointXY
    def forward(self,point):
        t = np.matmul(self.m,np.array([point.x(),point.y(),1]))
        return QgsPointXY(t[0],t[1])
    
    #QgsPointXY->QgsPointXY
    def reverse(self,point):
        t = np.matmul(self.inv,np.array([point.x(),point.y(),1]))
        return QgsPointXY(t[0],t[1])



def mag(v):
    return (v**2).sum()**0.5

#angle betwwen vectors. always positive.
def angle(v1,v2):
    return math.acos(np.dot(v1,v2)/(mag(v1)*mag(v2)))



#->affine
#3x3 affine transform with translation,rotation,scale from 2 points p and corrected points c.
#points as numpy array
#same scale for x and y.
#need x and y translations, the rotation angle, and the scale

def trs(p1,c1,p2,c2):
    p1 = np.array(p1,dtype = float)
    c1 = np.array(c1,dtype = float)

    v1 = np.array([p2[0]-p1[0],p2[1]-p1[1]],dtype = float)#original line
    v2 = np.array([c2[0]-c1[0],c2[1]-c1[1]],dtype = float)#corrected line
    
    s = mag(v2)/mag(v1)#scale factor
  #  print('s',s)
  
    a = angle(v1,v2)#angle for rotation
    #need negative angle where rotated anticlockwise
    if np.cross(v1,v2) < 0:
        a = -a
    
    r = np.zeros(shape = (3,3),dtype = float)
    r[0,0] = s*math.cos(a)
    r[0,1] = - s*math.sin(a)
    r[1,0] = s*math.sin(a)
    r[1,1] = s*math.cos(a)
    r[2,2] = 1
 #   print('r',r)

    #translation
    new1 = applyTransform(p1,r)
    print('new1',new1)
    tr = c1 - new1
    r[0,2] = tr[0]
    r[1,2] = tr[1]
 #   return np.matmul(r,t)
    return affine(r[0,0],r[0,1],r[0,2],r[1,0],r[1,1],r[1,2])
    

#array/list [x,y]
def applyTransform(xy,t):
    return np.matmul(t,np.array([xy[0],xy[1],1]))[0:2]


def fromTranslation(xShift,yShift):
    return affine(c = xShift, f = yShift)



if __name__ in ('__console__','__main__'):
    m = trs((5,5),(10,10),(10,10),(30,20))
    print('m',m)
   # p = np.array([5,5])
    new  = m.forward(QgsPointXY(5,5))
    print(new)
#    print('c2',applyTransform([7.5,7.5],m))
  #  print('mag',mag(np.array([3,4])))