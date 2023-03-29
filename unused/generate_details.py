# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 11:22:52 2022

@author: Drew.Bennett


functions for gtting image details from filePath.


"""

import os
import re

import json

rootGroup = 'image_loader'

#unused
#list of strings representing group hierarchy.
#same as folder hierarchy
#def generateGroupsFromFolder(file,folder,root=rootGroup):
  #  folder = os.path.dirname(folder)
  #  file = os.path.dirname(file)
    
  #  p = os.path.relpath(file,folder)
  #  g = p.split(os.sep)
   
   # if root:
  #     g.insert(0,root)
   
 #   return listToGroupString(g)


#str,str,str ->str
def generateGroups(run,imagetype,root=rootGroup):
    r = [root]
    r.append(imagetype)
    r.append(run)    
    return json.dumps(r)





#def generateGroupsList(fileName,root=rootGroup):
 #   r = [root]
 #   r.append(generateType(fileName))
 #   r.append(generateRun(fileName))
  #  return r


#assuming filenames are in form of run_type_imageId
#(start)(run)_(image_type)_(image_id)(end)


#name for layer
#filename without extention
#(run)_(image_id)
#def generateLayerName(filePath):
    #return os.path.splitext(os.path.basename(filePath))[0]
  #  return '{}_{}'.format(generateRun(filePath),generateImageId(filePath))


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


#findall()




#f = '100_6_ImageInt_000180.tif'
#print(generateRun(f))













#string representing groups to list.
#csv and database contain string.
#def groupStringToList(text):
 #   try:
#        return json.loads(text)
 #   except:
  #      print('Could not read groups from {t}. Reverting to empty list.'.format(t=text))
  #      return []


#def listToGroupString(groups):
 #   return json.dumps(groups)


#print(generateImageId(r'E:\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'))