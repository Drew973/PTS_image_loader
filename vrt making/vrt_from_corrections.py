# -*- coding: utf-8 -*-
"""
Created on Thu May 18 14:40:51 2023

@author: Drew.Bennett


Reads corrections csv.
Makes vrt for each run in this from corresponding .tif images in folder.
Also makes overviews. Making overviews is time consuming but speeds up rendering in QGIS.


"""

import csv
import os
#import glob
import re

import subprocess


#digits at end of filename without extention
# str -> int
def generateImageId(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('\d+$', name)
    if m:
        return int(m.group(0))
    else:
        return -1



from osgeo import gdal , gdalconst


    
def makeVrts(folder,corrections,createOverviews=False,ext='.tif'):
    
    images = {}
    for f in os.listdir(folder):
        if os.path.splitext(f)[-1] == ext:
            images[generateImageId(f)] = os.path.join(folder,f)
    
    
   # pattern = folder+'\*.tif'#. different glob versions?
  #  for f in glob.glob(pattern):    
    #    images[generateImageId(f)] = f
        
        
    with open(corrections,'r') as f:
        
        reader = list(csv.DictReader(f))
        
        for i,d in enumerate(reader):
            
            run = d['RunID']
            
            print('processing {v} of {t}'.format(v=i+1,t=len(reader)))
            
            vrt = os.path.join(folder,run+'.vrt')
         
            files = [images[image_id] for image_id in range(int(d['FromFrame']),int(d['ToFrame'])+1) if image_id in images]    

            if files:
        
                vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic',
                                                   bandList=[1],
                                                   outputSRS = 'EPSG:27700',
                                                   srcNodata = 0,
                                                   VRTNodata = 0)
                
                r = gdal.BuildVRT(vrt, files, options=vrt_options)
                band = r.GetRasterBand(1)
                if band:
                    band.SetColorInterpretation(gdalconst.GCI_GrayIndex)
    
                if createOverviews and r:
                    overviewCommand = 'gdaladdo "{f}" 128 256 516 -ro --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL --config GDAL_NUM_THREADS ALL_CPUS'.format(f=vrt)
                    subprocess.run(overviewCommand,creationflags=subprocess.CREATE_NO_WINDOW)
                   # r.BuildOverviews
    
                r.FlushCache()
                r = None
            else:
                print('No files found for run {run}'.format(run=run))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('folder')
    parser.add_argument('corrections')
   # parser.add_argument('-createOverviews',default=True)
    args = parser.parse_args()    
    makeVrts(args.folder,args.corrections)


#eg python "C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\vrt_from_corrections.py" "D:\RAF Shawbury\TIF Images\MFV1_005\ImageRng" "D:\RAF Shawbury\Processed Data\MFV1_005 Coordinate Corrections.csv"
#eg python "C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\vrt_from_corrections.py" "D:\RAF Shawbury\TIF Images\MFV1_005\ImageInt" "D:\RAF Shawbury\Processed Data\MFV1_005 Coordinate Corrections.csv"
#eg python "C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\vrt_from_corrections.py" "D:\RAF Shawbury\TIF Images\MFV1_005\hybrid" "D:\RAF Shawbury\Processed Data\MFV1_005 Coordinate Corrections.csv"
