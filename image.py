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
    def __init__(self,imageId = None,file='',georeferenced='',run = '',startM = None ,endM = None, offset = 0.0):
        
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
        
        if startM is None:
            startM = self.imageId * 5
        
        if endM is None:
            endM = self.imageId * 5 + 5
        
        self.startM = startM #in meters
        self.endM = endM #in meters
        self.offset = offset #in meters

        self.gcps = []
        self.temp = ''
        if not self.temp:
            self.temp = os.path.normpath(os.path.join(os.path.dirname(self.georeferenced),os.path.splitext(os.path.basename(self.georeferenced))[0]+'.vrt'))


      #image_loader,type,run
    @property
    def groups(self):
        return['image_loader',
                      self.imageType.name,
                      self.run]
    
    
    def translateCommand(self):
        return translateCommand(origonal = self.file,temp=self.temp,GCPs=self.gcps,grayscale = self.imageType in [types.intensity,types.rg])
            
            
    def warpCommand(self):
        return warpCommand(self.temp,self.georeferenced)
         
    
    #load into QGIS
    def load(self):
        name = os.path.splitext(os.path.basename(self.georeferenced))[0]
        #layer = QgsRasterLayer(self.georeferenced,name)
        layer = QgsRasterLayer(self.file,name)

        group = getGroup(self.groups)
        group.addLayer(layer)
        group.setExpanded(False)    
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




'''
    calculate GCPS treating image is rectangle. Where vehicle turned corner sensor follows curved path. this causes warping...
    GCPs are moved to right by offset
'''

def gcps(lineLayer,startField,endField,startM,endM,offset=0.0):
    
    startPoint = measureToPoint(lineLayer,startField,endField,startM)
    endPoint = measureToPoint(lineLayer,startField,endField,endM)
         
    
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
    



'''
    calculate GCPS treating image as curved path WIDTH wide.
'''
'''
#import numpy
from image_loader.get_line import getLine
from qgis.core import QgsGeometry

def gcps(lineLayer,startField,endField,startM,endM,offset=0.0):
    geom = getLine(lineLayer,startField,endField,startM,endM)#QgsGeometry
    
    #length = geom.length()
    
    r = []
    
    #left edge
    left = geom.offsetCurve(distance= offset-WIDTH * 0.5, segments = 64,joinStyle = QgsGeometry.JoinStyleRound, miterLimit=0.0)
    leftLength = left.length()
    d = 0
    last = None
    for v in left.vertices():
        if last is not None:
            d += v.distance(last)    
        last = v        
        line = LINES * ( 1 -d / leftLength )
        r.append(gdal.GCP(v.x(),v.y(),0,0,line)) #pixel = 0
        
        
    #right edge
    right = geom.offsetCurve(distance = offset+WIDTH * 0.5, segments = 64,joinStyle = QgsGeometry.JoinStyleRound, miterLimit=0.0)
    rightLength = right.length()
    d = 0
    last = None
    for v in right.vertices():
        if last is not None:
            d += v.distance(last)    
        last = v        
        line = LINES * (1 - d / rightLength )
        r.append(gdal.GCP(v.x(),v.y(),0,PIXELS,line)) #pixel = PIXELS for right of image
        
    return r
'''    


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


from qgis.utils import iface

def refreshLayers(files,group = QgsProject.instance().layerTreeRoot()):
    for i in group.findLayers():
        layer = i.layer()
        if layer:
            file = layer.dataProvider().dataSourceUri()
            if file in files:
                #layer.reload()
               # layer.triggerRepaint()
               
               # uri = layer.dataProvider().dataSourceUri()
               # layer.dataProvider().setDataSourceUri(None)
               # layer.dataProvider().updateExtents()

             #   layer.dataProvider().reloadData()
              #  layer.dataProvider().setDataSourceUri(uri)
               # layer.dataProvider().reloadData()
                layer.dataProvider().updateExtents()
                layer.dataProvider().reloadData()

               # layer.dataProvider().reload()
                layer.triggerRepaint()
    iface.mapCanvas().refresh()
    
    
    
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
    
    
from image_loader.measure_to_point import measureToPoint
    
   
#from image_loader.georeference import georeference


#'GDAL translate/edit command to add GCPS to raster'
def _GCPCommand(gcp):
    #-gcp <pixel> <line> <easting> <northing>
    return '-gcp {pixel} {line} {x} {y}'.format(pixel = gcp.GCPPixel,
        line = gcp.GCPLine,
        x = gcp.GCPX,
        y = gcp.GCPY)

def overviewCommand(file):
    return 'gdaladdo "{}" 2 4 8 16 --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL'.format(file)



def editCommand(file,gcps):
    g = ' '.join([_GCPCommand(gcp) for gcp in gcps])
    
    prog = r'C:\OSGeo4W\apps\Python39\Scripts\gdal_edit'
    return '"{prog}" "{file}" -ro -a_srs "EPSG:27700" -a_nodata 255 {gcp}'.format(file=file,gcp=g,prog=prog)



from subprocess import Popen,PIPE,CREATE_NO_WINDOW

import time

def remakeImages(images,progress,layer=None,startField=None,endField=None):
    if layer and startField and endField:
        
        #recalc points
        progress.setValue(0)
        progress.setLabelText('Calculating GPS positions')
        progress.setMaximum(len(images))
        
        for i,im in enumerate(images):
            if progress.wasCanceled():
                return  
            #im.startPoint = measureToPoint(layer,startField,endField,im.startM)
            #im.endPoint = measureToPoint(layer,startField,endField,im.endM)
            
            im.gcps = gcps(lineLayer = layer,
                 startField = startField,
                 endField = endField,
                 startM = im.startM,
                 endM = im.endM,
                 offset = im.offset)
            
            progress.setValue(i)
            
            
        #remove layers            
      #  progress.setLabelText('Removing layers')
      #  progress.setValue(0)
     #   removeSources([im.file for im in images])
        
        #georeference
        progress.setLabelText('Georeferencing images')
        progress.setValue(0)
        
        
        
        
        editCommands = [editCommand(im.file,im.gcps) for im in images]
     #   print(editCommands)
        processes = [Popen(c,stdout=PIPE, stderr=PIPE,creationflags = CREATE_NO_WINDOW,shell=True) for c in editCommands]
        
     #   st = time.time()#seconds
     #   t = 0
     #   timeout = 10 # seconds
        
     #   while t<timeout:
      #      t = time.time()-st
             #print(t)
      # #     time.sleep(1)
            
            
          #  progress.setValue(len([proc for proc in processes if proc.poll() is not None]))
         #   if progress.wasCanceled():
         #       for proc in processes:
         #           proc.terminate()
            
        #    v = 0
         #   for proc in processes:
         ##       if proc.poll() is not None:
                  #  v+=1
                    
         #   progress.setValue(v)
        for i,p in enumerate(processes):
             p.wait()
             if progress.wasCanceled():
                 for proc in processes:
                     proc.terminate()
                    
             
             progress.setValue(i)
             err = p.stderr.read()
             if err:
                 print(editCommands[i],err)
        
       # for i,im in enumerate(images):
           
            #georeference(file = im.file,GCPs = im.gcps)
          #  im.georeferenced = im.file
           # progress.setValue(i)
        progress.setLabelText('Refreshing layers')
        progress.setValue(0)
        refreshLayers([im.file for im in images])


#from subprocess import Popen,PIPE,CREATE_NO_WINDOW



'''
def translateImages(images,progress):
    progress.setLabelText('Translating images')
    progress.setMaximum(len(images))
    commands = [im.translateCommand() for im in images]
    runCommands(commands,progress)


def warpImages(images,progress):
    progress.setLabelText('Warping images')
    progress.setMaximum(len(images))
    commands = [im.warpCommand() for im in images]
    runCommands(commands,progress)
    

'''
   # run commands in paralell.
   # progress bar is rough guide.
def runCommands(commands,progress):
    progress.setMaximum(len(commands))
    progress.setValue(0)
    processes = [Popen(c,stdout=PIPE, stderr=PIPE,creationflags = subprocess.CREATE_NO_WINDOW,shell=True) for c in commands]
    for i,p in enumerate(processes):
        p.wait()
        if progress.wasCanceled():
            return  
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

