# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 14:27:55 2023

@author: Drew.Bennett
"""
import numpy



def bisector(v1,v2):
    return unitVector(leftPerp(v1)+leftPerp(v2))

#numpy array. m,x,y
#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5


#perpendicular vector to left.
#numpy.array -> numpy.array
def leftPerp(vector):
    return numpy.array([ - vector[1],vector[0]])



def distance(v1,v2):
    v = v1 - v2
    return (v**2).sum()**0.5



#beveled style. leftOffset negative for right hand side.
#same direction as g.
#spatialite offset_curve buggy,returning multilinestring
#qgsGeometry?


#-> array((x,y))
def offset(leftOffset,line):
  
   
    for row,pt in enumerate(line[1::-1],1):
        pt = line[row]
       # nextVect = line[row+1,:]-line[row,:]
        vect = line
        print(lastVect)
        print(nextVect)
        
        
     #   print('v',v)
   


if __name__ == '__main__':
    #print(offset(10,numpy.array([[0,0],[0,100]])))
    print(offset(10,[[0,0],[10,0],[10,20]]))
