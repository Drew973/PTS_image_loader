# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 11:22:52 2022

@author: Drew.Bennett
"""

import os
import re


from image_loader.group_functions import listToGroupString
from image_loader import constants


#list of strings representing group hierarchy.
#same as folder hierarchy
def generateGroupsFromFolder(file,folder,root=constants.rootGroup):
    folder = os.path.dirname(folder)
    file = os.path.dirname(file)
    
    p = os.path.relpath(file,folder)
    g = p.split(os.sep)
   
    if root:
        g.insert(0,root)
   
    return listToGroupString(g)



def generateGroups2(run,imagetype,root=constants.rootGroup):
    r = [root]
    r.append(imagetype)
    r.append(run)    
    return listToGroupString(r)


def generateGroups(fileName,root=constants.rootGroup):
    r = [root]
    r.append(generateType(fileName))
    r.append(generateRun(fileName))
    return listToGroupString(r)


#assuming filenames are in form of run_type_imageId
#(start)(run)_(image_type)_(image_id)(end)

#run_type_image_id

#name for layer
#filename without extention
def generateLayerName(filePath):
    return os.path.splitext(os.path.basename(filePath))[0]


#(start)(run)_(not_)_(digits)(end)
def generateRun(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('^.*(?=_[^_]+_\d+$)', name)
    if m:
        return m.group(0)
    else:
        return ''



#digits at end of filename without extention
def generateImageId(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('\d+$', name)
    if m:
        return m.group(0)
    else:
        return '-1'


#[{filePath,layerName,groups}] for each tif in folder.
def generateDetails(folder,createOverview=True):
    return [imageDetailsfromPath(f,folder,createOverview) for f in getFiles(folder,'.tif')]




def getFiles(folder,exts=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            if os.path.splitext(f)[1] in exts or exts is None:
                yield os.path.join(root,f)
                
                
#(start)(run)_(type)_(digits)(end)
def generateType(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('(?<=_)[^_]+(?=_\d+$)', name)#_(non _)_(digits)(end)
    if m:
        return m.group(0)
    else:
        return ''
                 

def imageDetailsfromPath(filePath,folder,createOverview=True):
    
    return {'run':generateRun(filePath),
            'image_id':generateImageId(filePath),
            'file_path':filePath,
            'groups':generateGroups(generateRun(filePath),generateType(filePath)),
            'name':generateLayerName(filePath)
            }



if __name__=='__main__' or __name__=='__console__':
    p = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'
    print(generateImageId(p))
    print(generateRun(p))
    
    
    folder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
    print(generateDetails(folder))