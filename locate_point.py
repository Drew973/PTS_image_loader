# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 12:42:41 2023

@author: Drew.Bennett
"""



def prevNextVertices(line,distance):    
    dist = 0
    last = line.vertexAt(0)
    for v in line.vertices():
        dist += v.distance(last)

        if dist<distance:
            last = v
    
        if dist>=distance:
            return (last,v)

    #None if distance > length


from qgis.core import QgsGeometry
import numpy


def locatePoint(line,startM,endM,point):

    d = line.lineLocatePoint(QgsGeometry.fromPointXY(point))
    m = startM + (endM-startM)*d/line.length()    
        
    nearest = line.interpolate(d).asPoint()
    
    if point.distance(nearest) == 0:
        return (m,0)
    
    p,n = prevNextVertices(line,d)
    v1 = numpy.array([n.x()-p.x(),n.y()-p.y()])
    v1 = v1 / numpy.linalg.norm(v1)
    #unit vector from last vertex to next vertex
    
    v2 = numpy.array([point.x()-nearest.x(),point.y()-nearest.y()])
        
    dotProd= numpy.dot(v1,v2)
   
    return (m,dotProd)
   
    
    
if __name__=='__console__':
    from qgis.core import QgsPointXY,QgsGeometry
    s = QgsPointXY(10,10)
    e = QgsPointXY(100,100)
    
    line = QgsGeometry.fromPolylineXY([s,e])
    r = locatePoint(line,0,1,s)
    print(r)#0,0
    
    r = locatePoint(line,0,1,QgsPointXY(100,110))
    print(r)
