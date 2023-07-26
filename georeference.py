# -*- coding: utf-8 -*-
"""
Created on Tue May 16 13:28:48 2023

@author: Drew.Bennett
"""

import os
#from qgis.core import QgsGeometry    
import argparse

#from shapely import from_wkb, from_wkt


from shapely import wkt
from shapely.geometry import Point,LineString
from osgeo import gdal,osr,gdalconst
import numpy


def warpedFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '_warped.tif'


noData = 255
WIDTH = 4.0
PIXELS = 1038
LINES = 1250


'''
dataset should have gcps OR geotransform , not both
use GCPs. geotransform is affine. Doesn't curve rectangle as it should.
translated has weird bits like repeated image. fine after warping.
rendering of vrt seems buggy with random crashes. COG seems to take about as long to write. use this.

need to call from osgeo4w shell. easier to import shapely from here.
jpg is much smaller.
lossy compression means some 'no data' pixels not. odd squares around boundary.
'''    
   
#create warped vrt from file
def georeferenceFile(file,centerLine):
    
    cl = wkt.loads(centerLine)

    if os.path.exists(file):
        gcps = _gcps(cl)
      #  for p in gcps:
        #    print(GCPCommand(p))
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(27700)
        srs = srs.ExportToWkt()
        translatedFile = '/vsimem/' + os.path.splitext(os.path.basename(file))[0] + '_translated.vrt'
       # translatedFile = os.path.splitext(file)[0] + '_translated.vrt'
        translated = gdal.Translate(translatedFile,
                                    file,
                                    GCPs = gcps,
                                    outputSRS = srs,
                                    noData = noData,
                                    bandList=[1])
  
        band = translated.GetRasterBand(1)
        band.SetColorInterpretation(gdalconst.GCI_GrayIndex)
        translated.FlushCache()
        dest = warpedFileName(file)
        ext = os.path.splitext(dest)[1]

        if ext == '.vrt':
        #VRT -b works in osgeo4w shell.
            gdal.Warp(destNameOrDestDS = dest,
                 srcDSOrSrcDSTab = translated,
                 resampleAlg = 'near',
                 tps = True,
                 dstalpha = True,
                 warpOptions = ['SKIP_NOSOURCE=YES']
        )
            
            #rewrite vrt replacing translated with original file. hacky but effective.
            with open(dest,'r') as f:
                newText = f.read().replace(translatedFile,file)
            with open(dest,'w') as f:
                 f.write(newText)
        
        if ext == '.tif':
            #-b works in osgeo4w shell.
            gdal.Warp(destNameOrDestDS = dest,
                     srcDSOrSrcDSTab = translated,
                     resampleAlg = 'near',
                     format = 'COG',
                     tps = True,
                     creationOptions = ['QUALITY=60','COMPRESS=JPEG','OVERVIEWS=IGNORE_EXISTING'],
               #      creationOptions = ['QUALITY=60','COMPRESS=LZW','OVERVIEWS=IGNORE_EXISTING','SPARSE_OK=TRUE'],

                     warpOptions = ['SKIP_NOSOURCE=YES']
            )
            #overviews are included in these. 
        translated = None
       # os.remove(translatedFile)
    else:
        raise ValueError('{file} not found'.format(file=file))
       



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

# g:LineString-> LineString
def offset(g,leftOffset):
    
    points = [numpy.array([p[0],p[1]]) for p in g.coords]
    offsetVects = []
    
    for i,p in enumerate(points[1:],1):
        v = p-points[i-1]
     #   print('v',v)
        offsetVects.append(leftOffset*unitVector(leftPerp(v)))
  #  print('offsetVects',offsetVects)
  
    #start point + offset vector    
    newPoints = [points[0]+offsetVects[0]]
    
    #beveled style. point+previous offset and point+next_offset per original point.
    for i,p in enumerate(points[1:-1],1):
        a = p+offsetVects[i-1]
        b = p+offsetVects[i]
        
        #add in order of distance to last point.
        if distance(newPoints[-1],b) < distance(newPoints[-1],a):
            newPoints += [b,a]
        else:
            newPoints += [a,b]
            
    newPoints.append(points[-1]+offsetVects[-1])
    
   #print('newPoints',newPoints)
    return LineString([Point(p[0],p[1]) for p in newPoints])


    


#calculate list of gdal gcps from center line. shapely geometry.
def _gcps(centerLine):
    left = offset(centerLine,0.5*WIDTH)
    right = offset(centerLine,-0.5*WIDTH)

   # print('left',left)
 #   print('right',right)

    r = []
    leftLength = left.length
    d = 0
    last = None
    for c in left.coords:
       # print(c)
        v = Point(c)
        if last is not None:
            d += v.distance(last)    
        last = v        
        line = LINES - (LINES * d / leftLength)
        r.append(gdal.GCP(v.x,v.y,0,0,line)) #pixel = 0
        
    rightLength = right.length
    d = 0
    last = None
    for c in right.coords:
        v = Point(c)
        if last is not None:
            d += v.distance(last)
        last = v        
        line = LINES - (LINES * d / rightLength)
        r.append(gdal.GCP(v.x,v.y,0,PIXELS,line)) #pixel = PIXELS for right of image
      
    return r



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('centerLine')
    args = parser.parse_args()    
    georeferenceFile(args.file,args.centerLine)
    
    
    #test
    #cd C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader
    #python georeference.py "C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\ImageInt\2023-01-21 10h08m11s LCMS Module 1 002706.jpg" "LineString (354460.98048886 321911.91561537, 354460.44945128 321912.71103371, 354459.90769109 321913.6895637, 354459.46776974 321914.74056117, 354459.16101983 321915.89710644, 354458.95654222 321917.10052758, 354458.9588284 321917.33043448)"
    #good test case. should be curved.
    #gdalinfo 2023-01-21 10h08m11s LCMS Module 1 002706.jpg
#    python georeference.py "D:/RAF Shawbury/Data\2023-01-20\MFV1_001\Run 2\LCMS Module 1\Images\RangeWithoutOverlay\2023-01-20 15h26m34s LCMS Module 1 000345.jpg" "LineString (355032.217416 321691.265424, 355032.216744 321692.259914, 355032.216072 321693.254404, 355032.2154 321694.248894, 355032.215403 321695.243378, 355032.214731 321696.237869)"
    