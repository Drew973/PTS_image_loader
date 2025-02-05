# -*- coding: utf-8 -*-
"""
needs to work as standalone.

have centerline. Curved line.
shape for image on map:
    rectangle leaves gaps. 
    geotransform only supports rectangle
    trapezium good compromize.

dataset should have gcps OR geotransform , not both
geotransform is affine. Doesn't curve rectangle as it should.
could write worldfile for original image if rectangle.

use GCPs.
translated has weird bits like repeated image. fine after warping.
rendering of vrt seems buggy with random crashes. COG seems to take about as long to write. use this.

need to call from osgeo4w shell.
jpg is much smaller.
lossy compression means some 'no data' pixels not causing odd squares around boundary.

-tps is thin plate transform. 
faster with fewer gcps and without this.

translate then warp.

use world file where curvature low? rendering performance?
 /vsimem/
gdal_translate {outputFile} {inputFile} -gcp <pixel> <line> <easting> <northing>

gdalwarp.exe
"""

import os
import argparse
from osgeo import gdal,osr,gdalconst
import json

gdal.UseExceptions()
noData = 255

def warpedFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '_warped.tif'

   
#create warped vrt from file
def georeferenceFile(file : str , warpedFile : str , gcps:list , srid : int):
    
    if os.path.exists(file):
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(srid)
        srs = srs.ExportToWkt()
        translatedFile = r'/vsimem/' + os.path.splitext(os.path.basename(file))[0] + '_translated.vrt'
       # translatedFile = '/vsimem/' + os.path.splitext(os.path.basename(file))[0] + '_translated.tif'#created on disk?
  
        
        #in memory File
       # translatedFile = os.path.splitext(file)[0] + '_translated.vrt'
        translated = gdal.Translate(translatedFile,
                                    file,
                                    GCPs = gcps,#list
                                    outputSRS = srs,
                                    noData = noData,
                                    bandList=[1])
  
        band = translated.GetRasterBand(1)
        band.SetColorInterpretation(gdalconst.GCI_GrayIndex)
        translated.FlushCache()
        ext = os.path.splitext(warpedFile)[1]

        if ext == '.vrt':
        #VRT -b works in osgeo4w shell.
            gdal.Warp(destNameOrDestDS = warpedFile,
                 srcDSOrSrcDSTab = translated,
                 resampleAlg = 'near',
             #    tps = True,
                 dstalpha = True,
             #    warpOptions = ['SKIP_NOSOURCE=YES']
                 warpOptions = ['SKIP_NOSOURCE=YES,overwrite=YES']

        )
            #rewrite vrt replacing translated with original file. hacky but effective.
            with open(warpedFile,'r') as f:
                newText = f.read().replace(translatedFile,file)
            with open(warpedFile,'w') as f:
                 f.write(newText)
        
        if ext == '.tif':
            #-b works in osgeo4w shell.
            gdal.Warp(destNameOrDestDS = warpedFile,
                     srcDSOrSrcDSTab = translated,
                     resampleAlg = 'near',
                     format = 'COG',
                     tps = True,
                   #  creationOptions = ['QUALITY=60','COMPRESS=JPEG','OVERVIEWS=IGNORE_EXISTING'],
                     creationOptions = ['COMPRESS=LZW','OVERVIEWS=IGNORE_EXISTING'],

                     warpOptions = ['SKIP_NOSOURCE=YES'],
                     warpMemoryLimit  = 10,#use upto 10mb. images~0.3mb
            )
            #overviews are included in these.
            
            #Thin plate spline vs Polynomial transform?
            #polynomial always seems to make rectangle
            
            
        translated = None
       # os.remove(translatedFile)
    else:
        raise ValueError('{file} not found'.format(file=file))
       
#GCP like (x,y,pixel,line)
def parseGcpString(s:str):
    return [gdal.GCP(r[0],r[1],0,r[2],r[3]) for r in json.loads(s)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('originalFile')
    parser.add_argument('warpedFile')
    parser.add_argument('gcp')#[(x,y,pixel,line)]
    parser.add_argument('srid')
    args = parser.parse_args()
    #x,y,z,pixel,line
    gcps = parseGcpString(args.gcp)
    georeferenceFile(args.originalFile , args.warpedFile , gcps , int(args.srid))


if __name__ in ('__main__','__console__'):
    #try profiling here.
    main()

