# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 08:04:01 2023

@author: Drew.Bennett
"""

import re
import os
import numpy

from glob import glob


'''
get string like MFV1_001 from filePath.
str->str
'''
def generateMfv(filePath):    
    r = re.findall('MFV\d*_\d*',filePath)
    if r:
        return r[-1]
    else:
        return ''
    
    
 
#digits at end of filename without extention
# str -> int
def generateImageId(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('\d+$', name)
    if m:
        return int(m.group(0))
    else:
        return -1
    
    
    
from enum import IntEnum

class types(IntEnum):
    intensity = 1
    rg = 2



#p:str -> types or None
def imageType(p):
    if 'IntensityWithoutOverlay' in p:
        return types.intensity
    
    if 'ImageInt' in p:
        return types.intensity
    
    
    if 'RangeWithoutOverlay' in p:
        return types.rg
    
    
    if 'ImageRng' in p:
        return types.rg
    
    
    


'''
find file for list of images.
id+type+mfv should be unique.
MFV in georeferenced filename D:\RAF Shawbury\TIF Images\MFV1_020\ImageInt\MFV1_020_ImageInt_000005.tif
and origonal name "D:\RAF Shawbury\Data\2023-01-22\MFV1_020\Run 11\LCMS Module 1\Images\IntensityWithoutOverlay\2023-01-22 10h15m22s LCMS Module 1 000005.jpg"

'''    
def findOrigonals(georeferenced,projectFolder):
    
    def key(f,mfv=None):
        if not mfv:
            mfv = generateMfv(f)
        return str(imageType(f))+'_'+str(generateImageId(f))+'_'+mfv
    
    
    mfvs = numpy.unique([generateMfv(g) for g in georeferenced])
    
    results = [''] * len(georeferenced)
    keys = [key(g) for g in georeferenced]
    
 
    for m in mfvs:
        pattern = "{project}/Data/**/{mfv}/**/Images/**/*.jpg".format(project=projectFolder,mfv = m)
    
        files = glob(pattern, recursive = True)
    
        for f in files:
            k = key(f,m)
            
            if k in keys:
                i = keys.index(k)
                results[i] = f
                
    return results

f = r"D:\RAF Shawbury\Data\2023-01-22\MFV1_020\Run 11\LCMS Module 1\Images\IntensityWithoutOverlay\2023-01-22 10h15m22s LCMS Module 1 000005.jpg"

#r = generateMfv(f)
#print(r)



f2 = r' D:\RAF Shawbury\TIF Images\MFV1_020\ImageInt\MFV1_020_ImageInt_000005.tif'
#r2 = generateMfv(f)
#print(r2)


print(findOrigonals([f2],r'D:\RAF Shawbury'))