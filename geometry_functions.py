# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 14:27:55 2023

@author: Drew.Bennett
"""
import numpy


def dist(x1,y1,x2,y2):
    return numpy.sqrt((x1-x2)*(x1-x2) + (y2-y1)*(y2-y1))
    

#perpendicular vector to left.
#numpy.array -> numpy.array
def leftPerp(vector):
    return numpy.array([ - vector[1],vector[0]])


#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5


def normalizeRows(a):
    s = a*a
   # print('s',s)
    rowSums = numpy.sqrt(s.sum(axis=1))
    #print('rowSums',rowSums)
    return a / rowSums[:, numpy.newaxis]


def testNormalize():
    a = numpy.array([[0,10],[0,100],[10,10],[-10,-10]])
    print(normalizeRows(a))
    
    
#vector from startPoint to endPoint of geom
def asVector(geom):
    line = geom.asPolyline()
    return numpy.array([line[1].x()-line[0].x(),line[1].y()-line[0].y()])


def bisector(v1,v2):
    return unitVector(leftPerp(v1)+leftPerp(v2))


def distance(v1,v2):
    v = v1 - v2
    return (v**2).sum()**0.5

def magnitude(v):
    return numpy.linalg.norm(v)


#(distance/linelength,offset)
#start = start point of line
#end: end point of line
#point x,y

#numpy array. start and end x,y. point :  numpy array x,y
def fractionAndOffset(start,end,point):
    se = end-start
    sp = point-start
    f = numpy.dot(se,sp)/numpy.sum(se*se)#fraction
    offset = numpy.cross(se,sp)/magnitude(se)
    return (f,offset)
    
        
def testFractionAndOffset():
    s = numpy.array([0,0])
    e = numpy.array([10,10])
    p = numpy.array([100,100])
    
    f = fractionAndOffset(s,e,p)
    print(f)