# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 14:38:37 2023

@author: Drew.Bennett



subclass QStandardItem?
id as parent item. Child item per attribute.




"""


#from qgis.core import QgsPointXY#QgsRasterLayer,QgsProject,QgsPoint#

import os
import re
from qgis.core import QgsRasterLayer,QgsPointXY
import csv
import subprocess
from image_loader.measure_to_point import measureToPoint

from image_loader.remake_image import translateCommand,warpCommand


WIDTH = 4.0
PIXELS = 1038
LINES = 1250
#LENGTH = 5.0
from enum import IntEnum

class types(IntEnum):
    intensity = 1
    rg = 2
    
    

class image:
    
    #run:str
    def __init__(self,imageId = None,file='',georeferenced='',run = ''):
        
        self.georeferenced = str(georeferenced)
        self.file = str(file)

        #file to get details from
        f = ''
        if self.georeferenced:
            f = self.georeferenced
        if self.file:
            f = self.file
            
        if not imageId:
            imageId = generateImageId(f)

        try:
            self.imageId = int(imageId)
        except:
            self.imageId = -1
        
        
        if run:
            self.run = str(run)
        else:
            self.run = generateRun(f)
                    
        self.imageType = imageType(f)
        
        self.startM = 0.0
        self.endM = 0.0
        self.offset = 0.0

        #calculate from layer. slow.
        self.startPoint = QgsPointXY()
        self.endPoint = QgsPointXY()
        
        self.temp = ''
        

      #image_loader,type,run
    @property
    def groups(self):
        return['image_loader',
                      self.imageType.name,
                      self.run]
    
    
    #remake georeferenced raster
    #set georeferenced to newFile
    #remake should not load/remove layers.
    
    def remake(self,to = ''):
        
        
        layers = []
       # groups = []
        data = []
        
        for i in QgsProject.instance().layerTreeRoot().findLayers():
            layer = i.layer()
            if layer:
                file = layer.dataProvider().dataSourceUri()
                if file == to:
                  #  sources.append(layer.dataProvider().dataSourceUri())
                #    groups.append(i)
                
                    layers.append(layer)
                    data.append(layer.dataProvider().dataSourceUri())
                   # groups.append()
                    layer.dataProvider().setDataSourceUri('')
             #       QgsProject.instance().removeMapLayer(layer.id())


        
        if not to:
            to = self.georeferenced
        
        if os.path.exists(self.file):
        
         #   if os.path.exists(to):
           #     removeSources(to)#unload layer so GDAL can rewrite it.
            
            gcps = GCPs(startPoint = self.startPoint,endPoint = self.endPoint,offset = self.offset)
           
            remakeImage(origonal = self.file,to=to,GCPs=gcps,grayscale = self.imageType in [types.intensity,types.rg])
           
            self.georeferenced = to
    
    
        #reset providers
        for i,layer in enumerate(layers):
            layer.dataProvider().setDataSourceUri(data[i])
           
           
        #    layer2 = QgsRasterLayer(s)
         #   groups[i].addLayer(layer2)
          #  QgsProject.instance().addMapLayer(layer2,False)#don't immediatly add to legend
           # node = groups[i].findLayer(layer2)
            #node.setItemVisibilityChecked(True)
            #node.setExpanded(False)    
            
            layer.reload()
            layer.triggerRepaint()
    
    
    
    def translateCommand(self):
        gcps = GCPs(startPoint = self.startPoint,endPoint = self.endPoint,offset = self.offset)
        return translateCommand(origonal = self.file,temp=self.temp,GCPs=gcps,grayscale = self.imageType in [types.intensity,types.rg])

            
            
    def warpCommand(self):
        return warpCommand(self.temp,self.georeferenced)
            
    
    #recalculate start/end point from layer and start/end m values.
    def recalcPoints(self,layer,field):
        self.startPoint = measureToPoint(layer = layer,field=field , m  = self.startM)
        self.endPoint = measureToPoint(layer = layer,field=field , m  = self.endM)
    
    
    #load into QGIS
    def load(self):
        name = os.path.splitext(os.path.basename(self.georeferenced))[0]
        layer = QgsRasterLayer(self.georeferenced,name)
        group = getGroup(self.groups)
        group.addLayer(layer)
        QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
        node = group.findLayer(layer)
        node.setItemVisibilityChecked(True)
        node.setExpanded(False)    
    
    
    
    
    #self<other
    def __lt__(self,other):
        
        if self.run<other.run:
            return True
        
        if self.imageId<other.imageId:
            return True
        
     #   if self.file<other.file:
          #  return True
        #
        return False
        
        
      #  return self.run <= other.run and self.imageId<other.imageId
        
        
    def __eq__(self,other):
        return self.run == other.run and self.imageId == other.imageId and self.file == other.file
    
    
    def __repr__(self):
        d = {'imageId':self.imageId,'run':self.run,'file':self.file,'georeferenced':self.georeferenced,'groups':self.groups}
        return 'image:'+str(d)
    
    
def fromCsv(file):        
    ext = os.path.splitext(file)[-1]
    if ext in ['.csv','.txt']:
             #  self.addDetails([d for d in image_details.fromCsv(file)])
    
        with open(file,'r',encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [name.lower().replace('_','') for name in reader.fieldnames]#lower case keys/fieldnames                 
            for d in reader:
                p = d['filepath']
                if os.path.isabs(p):
                    filePath = p
                else:
                    filePath = os.path.normpath(os.path.join(file,p))#from file not folder
                                            
                yield image(georeferenced = filePath,
                    run = find(d,'runid')#None
                    )    
    
from image_loader.geometry_functions import pointToVector,vectorToPointXY,unitVector,perpendicular
    
from osgeo import gdal




#calculate GCPs for image from start and endPoints
#GCPs are moved to right by offset

#startPoint:QgsPoint,endPoint:Qgspoint -> gdal.GCP
def GCPs(startPoint,endPoint,offset = 0):
    s = pointToVector(startPoint)
    e = pointToVector(endPoint)
            
    right = unitVector(perpendicular(e-s))#perpendicular to se
    offset = offset*right#shift all corners by ths
            
    TR = vectorToPointXY(offset + e + 0.5*WIDTH * right)
    TL = vectorToPointXY(offset + e - 0.5*WIDTH * right)
    BR = vectorToPointXY(offset + s + 0.5*WIDTH * right)
    BL = vectorToPointXY(offset + s - 0.5*WIDTH * right)
            
            ##GCPX,GCPY,GCPZ,GCPPixel,GCPLine
    return [gdal.GCP(TL.x(),TL.y(),0,0,0),
             gdal.GCP(TR.x(),TR.y(),0,PIXELS,0),
             gdal.GCP(BL.x(),BL.y(),0,0,LINES),
             gdal.GCP(BR.x(),BR.y(),0,PIXELS,LINES)]



#'GDAL translate command to add GCPS to raster'
def GCPCommand(gcp):
    #-gcp <pixel> <line> <easting> <northing>
    return '-gcp {pixel} {line} {x} {y}'.format(pixel = gcp.GCPPixel,
        line = gcp.GCPLine,
        x = gcp.GCPX,
        y = gcp.GCPY)


from qgis.core import QgsProject


def removeSources(files,group = QgsProject.instance().layerTreeRoot()):
    for i in group.findLayers():
        layer = i.layer()
        if layer:
            file = layer.dataProvider().dataSourceUri()
            if file in files:
                QgsProject.instance().removeMapLayer(i.layer().id())


#assume type and id do not contain _ charactor
#str->str
def generateRun(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    
    r = re.findall('\A.*(?=_[^_]+_\d+$)',name)
    
    if r:
        return r[-1]
    else:
        return ''
    
    
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
    
    
    
from qgis.core import QgsProject,QgsLayerTreeGroup


#str->str
#(start)(run)_(type)_(digits)(end)
def generateType(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('(?<=_)[^_]+(?=_\d+$)', name)#_(non _)_(digits)(end)
    if m:
        return m.group(0)
    else:
        return ''
    
    
'''
returns new or existing QgsLayerTreeGroup with name child and parent
#child:str
#parent:QgsLayerTreeGroup or QgsLayerTree
'''
def findOrMake(child,parent=QgsProject.instance().layerTreeRoot()):
    for c in parent.children():
        if c.name() == child and isinstance(c,QgsLayerTreeGroup):
            return c
    
    return parent.addGroup(child)
    


#finds or makes group from list of ancestors.
#groups: list of strings
def getGroup(groups):
    parent = QgsProject.instance().layerTreeRoot()
    for name in groups:
        parent = findOrMake(name,parent)
    return parent




    
    
def getFiles(folder,exts=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            if os.path.splitext(f)[1] in exts or exts is None:
                yield os.path.join(root,f)






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
    
def key(file):
    return str(imageType(file))+str(imageId(file)+generateRun(file))



                        
 #lookup value from dict, returning default if not present
def find(d,k,default=None):
    if k in d:
        return d[k]
    return default
            

from image_loader import image_functions
'''
find file for list of images.
root is folder to search
'''
def origonalFiles(images,root = None):
    georeferenced = [im.georeferenced for im in images]
    origonals = image_functions.findOrigonals(georeferenced,projectFolder=root)
    for i,im in enumerate(images):
        im.file = origonals[i]
    
    
        
    
from subprocess import Popen,PIPE
   

#todo: run multiple commands in paralell
#todo: calculate GCPS more efficiently. getFeatures() slow.
def remakeImages(images,progress,layer=None,startField=None,endField=None):
    
    progress.setMaximum(len(images))

    for i,im in enumerate(images):
        if progress.wasCanceled():
            return  
        if layer and startField:
            im.recalcPoints(layer=layer,field=startField)
        
     #   to = im.georeferenced
        if not im.temp:
            im.temp = os.path.join(os.path.dirname(im.georeferenced),os.path.basename(im.georeferenced)+'.vrt')
    
    translateImages(images,progress)
    warpImages(images,progress)
        
        

def translateImages(images,progress):
    progress.setLabelText('Translating images')
    commands = [im.translateCommand() for im in images]
    runCommands(commands,progress)


def warpImages(images,progress):
    progress.setLabelText('Warping images')
    commands = [im.warpCommand() for im in images]
    runCommands(commands,progress)
    

'''
    run commands in paralell.
    progress bar is rough guide.
'''
def runCommands(commands,progress):
    progress.setMaximum(len(commands))
    progress.reset()
    processes = [Popen(c,stdout=PIPE, stderr=PIPE,creationflags = subprocess.CREATE_NO_WINDOW) for c in commands]
    for i,p in enumerate(processes):
        p.wait()
        progress.setValue(i)
        err = p.stderr.read()
        if err:
            print(commands[i],err)


#digits at end of filename without extention
# str -> int
def imageId(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('\d+$', name)
    if m:
        return int(m.group(0))
    else:
        return -1
