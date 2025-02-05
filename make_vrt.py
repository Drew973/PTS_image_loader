# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 15:56:03 2025

@author: Drew.Bennett
"""

from osgeo import gdal
import json
import argparse
import sys



gdal.UseExceptions()
#vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True)
def makeVrtFile(vrtFile,files):
    gdal.SetConfigOption("COMPRESS_OVERVIEW", "LZW")#lossless compression
    gdal.SetConfigOption("INTERLEAVE_OVERVIEW", "PIXEL")   
    gdal.BuildVRT(vrtFile, files)
    ds = gdal.Open(vrtFile, 0)  # 0 = read-only, 1 = read-write. 
    factors = [32,64,128,256,512]
    ds.BuildOverviews("AVERAGE" , factors)
    ds = None



if __name__ in ('__main__','__console__'):
    sys.stderr.write('test error')
    sys.stderr.flush()
    raise ValueError('test error')
    parser = argparse.ArgumentParser()
   # parser.add_argument('rootFolder')
    parser.add_argument('vrtFile') # filepath
    parser.add_argument('fileList') # JSON list
    args = parser.parse_args()
    files = json.loads(args.fileList)
    sys.stdout.write('files:'+str(files))
    #print('files:' , files)
    makeVrtFile(args.vrtFile , files)