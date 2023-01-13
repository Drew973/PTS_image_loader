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


def generateGroupsList(fileName,root=rootGroup):
    r = [root]
    r.append(generateType(fileName))
    r.append(generateRun(fileName))
    return r


#assuming filenames are in form of run_type_imageId
#(start)(run)_(image_type)_(image_id)(end)


#name for layer
#filename without extention
#(run)_(image_id)
def generateLayerName(filePath):
    #return os.path.splitext(os.path.basename(filePath))[0]
    return '{}_{}'.format(generateRun(filePath),generateImageId(filePath))


#(start)(run)_(not_)_(digits)(end)


'''
#run containing _
#start of string followed by

#assume type and id do not contain _ charactor
def generateRun_old(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('\A.*(?=_[^_]+_\d+$)', name)
    if m:
        return m.group(0)
    else:
        return ''
#findall()
'''

#assume type and id do not contain _ charactor
def generateRun(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    
    r = re.findall('\A.*(?=_[^_]+_\d+$)',name)
    
    if r:
        return r[-1]
    else:
        return ''
#findall()




#f = '100_6_ImageInt_000180.tif'
#print(generateRun(f))


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



