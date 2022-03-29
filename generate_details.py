# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 11:22:52 2022

@author: Drew.Bennett
"""

import os

from image_loader.group_functions import listToGroupString
from image_loader import constants


#list of strings representing group hierarchy.
#same as folder hierarchy
def generateGroups(file,folder,root=constants.rootGroup):
    folder = os.path.dirname(folder)
    file = os.path.dirname(file)
    
    p = os.path.relpath(file,folder)
    g = p.split(os.sep)
   
    if root:
        g.insert(0,root)
   
    return listToGroupString(g)


#name for layer
#filename without extention
def generateLayerName(filePath):
    return os.path.splitext(os.path.basename(filePath))[0]


#folder name 2 levels up from file
def generateRun(filePath):
    return os.path.split(os.path.dirname(os.path.dirname(filePath)))[-1]        


#last 6 digits of filename without extention
def generateImageId(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    return int(name[-6:])
    

#[{filePath,layerName,groups}] for each tif in folder.
def generateDetails(folder,createOverview=True):
    return [imageDetailsfromPath(f,folder,createOverview) for f in getFiles(folder,'.tif')]




def getFiles(folder,exts=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            if os.path.splitext(f)[1] in exts or exts is None:
                yield os.path.join(root,f)
                
                
                 

def imageDetailsfromPath(filePath,folder,createOverview=True):
    
    return {'run':generateRun(filePath),
            'image_id':generateImageId(filePath),
            'file_path':filePath,
            'groups':generateGroups(filePath,folder),
            'name':generateLayerName(filePath)
            }                



if __name__=='__main__' or __name__=='__console__':
    p = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'
    print(generateImageId(p))
    print(generateRun(p))
    
    
    folder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
    print(generateDetails(folder))