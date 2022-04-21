# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 11:22:52 2022

@author: Drew.Bennett
"""

import os
import re

import json

rootGroup = 'image_loader'

#unused
#list of strings representing group hierarchy.
#same as folder hierarchy
def generateGroupsFromFolder(file,folder,root=rootGroup):
    folder = os.path.dirname(folder)
    file = os.path.dirname(file)
    
    p = os.path.relpath(file,folder)
    g = p.split(os.sep)
   
    if root:
        g.insert(0,root)
   
    return listToGroupString(g)



def generateGroups2(run,imagetype,root=rootGroup):
    r = [root]
    r.append(imagetype)
    r.append(run)    
    return listToGroupString(r)



def generateGroups(fileName,root=rootGroup):
    r = [root]
    r.append(generateType(fileName))
    r.append(generateRun(fileName))
    return listToGroupString(r)


#assuming filenames are in form of run_type_imageId
#(start)(run)_(image_type)_(image_id)(end)

#run_type_image_id

#name for layer
#filename without extention
#(run)_(image_id)
def generateLayerName(filePath):
    #return os.path.splitext(os.path.basename(filePath))[0]
    return '{}_{}'.format(generateRun(filePath),generateImageId(filePath))


#(start)(run)_(not_)_(digits)(end)
def generateRun(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('^.*(?=_[^_]+_\d+$)', name)
    if m:
        return m.group(0)
    else:
        return ''



#digits at end of filename without extention
#returns int
def generateImageId(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('\d+$', name)
    if m:
        return int(m.group(0))
    else:
        return '-1'



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



#string representing groups to list.
#csv and database contain string.
def groupStringToList(text):
    try:
        return json.loads(text)
    except:
        print('Could not read groups from {t}. Reverting to empty list.'.format(t=text))
        return []


def listToGroupString(groups):
    return json.dumps(groups)



if __name__=='__main__' or __name__=='__console__':
    p = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'
    print(generateImageId(p))
    print(generateRun(p))
    print(generateLayerName(p))
    
    folder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
