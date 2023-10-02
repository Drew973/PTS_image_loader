# -*- coding: utf-8 -*-
"""
Created on Tue May 16 13:28:48 2023

@author: Drew.Bennett
"""

import os
import argparse


from osgeo import gdal,osr,gdalconst


def warpedFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '_warped.tif'


noData = 255
WIDTH = 4.0
PIXELS = 1038
LINES = 1250


'''
dataset should have gcps OR geotransform , not both
geotransform is affine. Doesn't curve rectangle as it should.
could write worldfile for original image if rectangle not big issue.

use GCPs.
translated has weird bits like repeated image. fine after warping.
rendering of vrt seems buggy with random crashes. COG seems to take about as long to write. use this.

need to call from osgeo4w shell.
jpg is much smaller.
lossy compression means some 'no data' pixels not causing odd squares around boundary.

-tps is thin plate transform. 
faster with fewer gcps and without this.

'''    
   
#create warped vrt from file
def georeferenceFile(file,warpedFile,gcps):
    
    if os.path.exists(file):
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
        ext = os.path.splitext(warpedFile)[1]

        if ext == '.vrt':
        #VRT -b works in osgeo4w shell.
            gdal.Warp(destNameOrDestDS = warpedFile,
                 srcDSOrSrcDSTab = translated,
                 resampleAlg = 'near',
                 tps = True,
                 dstalpha = True,
                 warpOptions = ['SKIP_NOSOURCE=YES']
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
                     creationOptions = ['QUALITY=60','COMPRESS=JPEG','OVERVIEWS=IGNORE_EXISTING'],
                     warpOptions = ['SKIP_NOSOURCE=YES'],
            )
            #overviews are included in these.
            
            #Thin plate spline vs Polynomial transform?
            #polynomial always seems to make rectangle
            
            
        translated = None
       # os.remove(translatedFile)
    else:
        raise ValueError('{file} not found'.format(file=file))
       

#file:file,pixel[],line:[],x:[],y:[]


if __name__ == '__main__':
    import ast
    parser = argparse.ArgumentParser()
    parser.add_argument('originalFile')
    parser.add_argument('warpedFile')
    parser.add_argument('gcp')#[(x,y,pixel,line)]
    args = parser.parse_args()    
    
    #  #x,y,z,pixel,line
    gcps = [gdal.GCP(r[0],r[1],0,r[2],r[3]) for r in ast.literal_eval(args.gcp)]
    
    georeferenceFile(args.originalFile,args.warpedFile,gcps)

