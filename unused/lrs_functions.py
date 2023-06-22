# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 10:35:30 2023

@author: Drew.Bennett


getChainage should be exact inverse of getPoint


"""




#import shapely
#from shapely.geometry import Point,MultiLineString
#from shapely.geometry import shortest_line
#from shapely import shortest_line


from qgis.core import QgsGeometry,QgsPointXY




def geomFromLineString(line):
    return QgsGeometry.fromPolyline(line.vertices())

def toParts(g):
    for part in g.constParts():
        yield geomFromLineString(part)


def offsetLine(geom,distance):
    g = geom.offsetCurve(distance,128,QgsGeometry.JoinStyleRound,0)    #performance vs accuracy?
    if distance>0:
        return g
    else:
        return QgsGeometry.fromPolylineXY(reversed(g.asPolyline()))
    #offsetCurve reverses direction


#nearest line of multilinestring to pt
#(line:QgsGeometry,pt:QgsGeometry)->QgsGeometry
def nearestPart(line,pt):
    if line.isMultipart():       
        parts = [part for part in toParts(line)]
     #   print(parts)
        distances = [part.distance(pt) for part in parts]
        val, i = min((val, i) for (i, val) in enumerate(distances))
        return parts[i]
    return line


#geom:QgsGeometry->qgsPoint
def startPoint(geom):
    for v in geom.vertices():
        return v

##geom:QgsGeometry->qgsPoint
def endPoint(geom):
    for v in geom.vertices():
        pass
    return v
    
    

#wkt point and linestringM
# str,str ->(chainage:float,offset:float)
def getChainage(x,y,line):
    pt = QgsGeometry.fromPointXY(QgsPointXY(x,y))

    line = nearestPart(QgsGeometry.fromWkt(line),pt)
    
    startM = startPoint(line).m()
    endM = endPoint(line).m()
    
    dist = line.distance(pt)    
    
    left = offsetLine(line,dist)
    
    right = offsetLine(line, - dist)
    
    if pt.distance(left)<pt.distance(right):
        ol = left
        offset = dist
    #negative offset for right
    else:
        ol = right
        offset = - dist
        
    return (startM + (endM-startM)*ol.lineLocatePoint(pt)/ol.length(),offset)


#line:wkt LinestringM, offset:float->QgsPointXY
def getPoint(line,m,offset):
    geom = QgsGeometry.fromWkt(line)
    
    line = offsetLine(geom,offset)
    startM = startPoint(geom).m()
    endM = endPoint(geom).m()
    p = line.interpolate(line.length()*(m-startM)/abs(endM-startM)).asPoint()
    return p
    
        
from qgis.gui import QgsVertexMarker
from qgis.utils import iface


if __name__ in ('__main__','__console__'):
    
    try:
        iface.mapCanvas().scene().removeItem(marker1)
        iface.mapCanvas().scene().removeItem(marker2)
    except Exception:
        pass
        
    line = 'LINESTRING(354462.117965 321922.242824, 354462.105727 321922.217418, 354461.687255 321921.246843, 354461.358909 321920.278912, 354461.122475 321919.253721, 354460.967626 321918.205208, 354460.957894 321917.226475)'
    startM = 0
    endM = 1000
    
    pt = QgsPointXY(354445.563,321924.132)
    marker1 = QgsVertexMarker(iface.mapCanvas())
    marker1.setCenter(pt)
    
    
    ch,offset = getChainage(x = pt.x(),y=pt.y(),line = line,startM=startM,endM=endM)
    print(ch,offset)
    
    p2 = getPoint(line,startM,endM,ch,offset)
    marker2 = QgsVertexMarker(iface.mapCanvas())
    marker2.setCenter(p2)
    
    print('error of :{e} m'.format(e=pt.distance(p2)))
    
    
   # iface.mapCanvas().scene().removeItem(marker1)
   # iface.mapCanvas().scene().removeItem(marker2)

    