# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 13:00:26 2023

@author: Drew.Bennett
"""

import os
from osgeo import gdal


def makeVrt(vrtFile,listFile):
    
    
   # print(vrtFile,folder,files)
    
    #create directory for vrt file if necessary
    if not os.path.isdir(os.path.dirname(vrtFile)):
        os.makedirs(os.path.dirname(vrtFile))
    
    #remove overview if exists
    overview = vrtFile+'.ovr'
    if os.path.isfile(overview):
        os.remove(overview)
    
    
    #files = [os.path.join(folder,file) for file in files]
    
    dest = gdal.BuildVRT(vrtFile, listFile)
    
    
    if dest is not None:         
        #build overview for vrt.
        gdal.SetConfigOption("COMPRESS_OVERVIEW", "JPEG")
     #   dest.BuildOverviews("AVERAGE", [])#remove existing overviews. prevent them growing every time vrt made.
     #removes vrt?!
     
        dest.BuildOverviews("AVERAGE", [32,64,128,256,512])
    
    else:
        print('unknown error writing VRT')
        
    #dest.FlushCache()# make sure written to disk. 
    dest = None#documentation says this should write to disk. Doesn't seem to.
#writes .ovr but not vrt file?!


    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vrtFile')
    parser.add_argument('listFile')
    args = parser.parse_args()
    makeVrt(args.vrtFile,args.listFile)