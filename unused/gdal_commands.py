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
    return '-gcp {pixel} {line} {x} {y}'.format(pixel = int(gcp.GCPPixel),
        line = int(gcp.GCPLine),
        x = gcp.GCPX,
        y = gcp.GCPY)



def old_gcps(geom,offset):
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
    
    

def _gcps(left,right):
    r = []
    
    #left edge
    leftLength = left.length()
    d = 0
    last = None
    for v in left.vertices():
        if last is not None:
            d += v.distance(last)    
        last = v        
        line = LINES * ( 1 -d / leftLength )
        r.append(gdal.GCP(v.x(),v.y(),0,0,line)) #pixel = 0
        
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









    
    #-a_ulurll ulx uly urx ury llx lly with edit or translate?
    
import os

from image_loader import georeference

noData = 0

# georeference && warp && overview
    
#(file:str,line:QgsGeometry) -> str
def georeferenceCommand(file,left,right):
 #   gcps = _gcps(geom=geom,offset=offset)
  #  gcpCommands = [GCPCommand(gcp) for gcp in gcps]
 #   dest = os.path.splitext(file)[0] + '.vrt'
    return 'python "{script}" "{file}" "{geom}"'.format(script = georeference.__file__,file = file, geom = geom)
   # return 'gdal_translate "{f}" "{dest}" -of VRT -if JPG -a_srs "EPSG:27700" -b 1 -colorinterp_1 gray -a_nodata {nd} {g}'.format(g=' '.join(gcpCommands),f=file,dest=dest,nd=noData)
   # return c


#'warp' into vrt
def warpCommand(file):
    dest = os.path.splitext(file)[0] + '.vrt'
    return 'gdalwarp "{source}" "{dest}" -s_srs "EPSG:27700" -t_srs "EPSG:27700" -srcnodata {nd} -dstnodata {nd} -r bilinear -overwrite'.format(source=file,dest=dest,nd=noData)



def overviewCommand(file):
    return 'gdaladdo "{f}" --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL'.format(f = file)
