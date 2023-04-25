# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 09:43:32 2023

@author: Drew.Bennett
"""

WIDTH = 4.0
PIXELS = 1038
LINES = 1250


from qgis.core import QgsGeometry
from osgeo import gdal



#'GDAL translate command to add GCPS to raster'
def GCPCommand(gcp):
    #-gcp <pixel> <line> <easting> <northing>
    return '-gcp {pixel} {line} {x} {y}'.format(pixel = gcp.GCPPixel,
        line = gcp.GCPLine,
        x = gcp.GCPX,
        y = gcp.GCPY)



def _gcps(geom,offset):
    r = []
    
    #left edge
    left = geom.offsetCurve(distance= offset-WIDTH * 0.5, segments = 64,joinStyle = QgsGeometry.JoinStyleRound, miterLimit=0.0)
    leftLength = left.length()
    d = 0
    last = None
    for v in left.vertices():
        if last is not None:
            d += v.distance(last)    
        last = v        
        line = LINES * ( 1 -d / leftLength )
        r.append(gdal.GCP(v.x(),v.y(),0,0,line)) #pixel = 0
        
        
    #right edge
    right = geom.offsetCurve(distance = offset+WIDTH * 0.5, segments = 64,joinStyle = QgsGeometry.JoinStyleRound, miterLimit=0.0)
    rightLength = right.length()
    d = 0
    last = None
    for v in right.vertices():
        if last is not None:
            d += v.distance(last)    
        last = v        
        line = LINES * (1 - d / rightLength )
        r.append(gdal.GCP(v.x(),v.y(),0,PIXELS,line)) #pixel = PIXELS for right of image
        
    return r
    
    
    
    
#(file:str,line:QgsGeometry) -> str
def georeferenceCommand(file,geom,offset):
    gcps = _gcps(geom=geom,offset=offset)
    print('gcps',gcps)
    