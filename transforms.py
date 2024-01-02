# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 09:00:54 2023

@author: Drew.Bennett
"""


import numpy as np
import math

def mag(v):
    return (v**2).sum()**0.5

#angle betwwen vectors. always positive.
def angle(v1,v2):
    return math.acos(np.dot(v1,v2)/(mag(v1)*mag(v2)))






#affine transform with translation,rotation,scale from 2 points p and corrected points c.
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
    
    r = np.zeros(shape = (2,3),dtype = float)
  #  r[2,2] = 1
    
    r[0,0] = s*math.cos(a)
    r[0,1] = - s*math.sin(a)
    r[1,0] = s*math.sin(a)
    r[1,1] = s*math.cos(a)
 #   print('r',r)

    #translation
    new1 = applyTranslation(p1[0],p1[1],r)
 #   print('new1',new1)
    tr = c1 - new1
    r[0,2] = tr[0]
    r[1,2] = tr[1]
 #   return np.matmul(r,t)
    return r

    
def applyTranslation(x,y,t):
    return np.matmul(t,np.array([x,y,1]))


if __name__ in ('__console__','__main__'):  
    m = trs((5,5),(10,10),(10,10),(30,20))
    print('m',m)
   # p = np.array([5,5])
    new  = applyTranslation(5,5,m)
    print(new)
    print('c2',applyTranslation(7.5,7.5,m))
  #  print('mag',mag(np.array([3,4])))