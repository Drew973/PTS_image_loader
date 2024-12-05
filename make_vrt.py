# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 11:23:11 2024

@author: Drew.Bennett
"""

from osgeo import gdal

#vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True)


def makeVrt(vrtFile,files,run,image_type):
    gdal.SetConfigOption("COMPRESS_OVERVIEW", "JPEG")
    gdal.SetConfigOption("INTERLEAVE_OVERVIEW", "PIXEL")   
    gdal.BuildVRT(vrtFile, files)
    ds = gdal.Open(vrtFile, 0)  # 0 = read-only, 1 = read-write. 
    factors = [32,64,128,256,512]
    ds.BuildOverviews("AVERAGE" , factors)
    ds = None
    
    
    
    
if __name__ in ('__main__','__console__'):
    
    d = {'vrtFile': 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\rg_1.vrt', 'files': ['D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002703_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002704_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002705_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002706_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002707_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002708_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002709_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002710_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002711_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002712_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002713_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002714_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002715_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002716_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002717_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002718_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002719_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002720_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002721_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002722_warped.tif', 'D:\\image_loader_demo\\test\\1_007\\ImageRng\\2023-01-21 10h08m11s LCMS Module 1 002723_warped.tif']}
    
    makeVrt(d['vrtFile'],d['files'],1,'range')