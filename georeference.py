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
from shapely.geometry import Point
from osgeo import gdal,osr,gdalconst




def warpedFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '_warped.vrt'



noData = 255

  
'''
dataset should have gcps OR geotransform , not both
use GCPs. geotransform is affine. Doesn't curve rectangle as it should.

translated has weird bits like repeated image. fine after warping.
'''    
   
#create warped vrt from file
def georeferenceFile(file,left,right):
    
    left = wkt.loads(left)
    right = wkt.loads(right)

        
    if os.path.exists(file):
        gcps = _gcps(left,right)
        
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

        #-b works in osgeo4w shell.
        gdal.Warp(destNameOrDestDS = dest,
                 srcDSOrSrcDSTab = translated,
                 resampleAlg = 'near',
                 tps = True,
                 warpOptions = ['SKIP_NOSOURCE=YES']
        )
        
     #   gdal.Warp(destNameOrDestDS = dest,
      #            srcDSOrSrcDSTab = source,
     #             format = 'COG',
      #            creationOptions = ['QUALITY=70','COMPRESS=JPEG','OVERVIEWS=IGNORE_EXISTING','SPARSE_OK=TRUE'])
        
        #-of COG -co COMPRESS=JPEG -co OVERVIEWS=IGNORE_EXISTING -co QUALITY=70 -co SPARSE_OK=TRUE
        translated = None
        
       #rewrite vrt replacing translated with original file. hacky but effective.
        with open(dest,'r') as f:
            newText = f.read().replace(translatedFile,file)
        with open(dest,'w') as f:
            f.write(newText)
            
        os.remove(translatedFile)

            
    else:
        raise ValueError('{file} not found'.format(file=file))
       
    
   
WIDTH = 4.0
PIXELS = 1038
LINES = 1250

#calculate list of gdal gcps from center line. shapely geometry.
def _gcps(left,right):
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
    parser.add_argument('left')
    parser.add_argument('right')
    args = parser.parse_args()    
    georeferenceFile(args.file,args.left,args.right)
    
    
    #test
    #cd C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader
    #python georeference.py "C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\ImageInt\2023-01-21 10h08m11s LCMS Module 1 002706.jpg" "LineString (354460.98048886 321911.91561537, 354460.44945128 321912.71103371, 354459.90769109 321913.6895637, 354459.46776974 321914.74056117, 354459.16101983 321915.89710644, 354458.95654222 321917.10052758, 354458.9588284 321917.33043448)"
    #good test case. should be curved.
    #gdalinfo 2023-01-21 10h08m11s LCMS Module 1 002706.jpg
    
    