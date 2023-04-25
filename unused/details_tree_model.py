# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 12:00:08 2023

@author: Drew.Bennett

tree model to store details and run info

"""

from PyQt5.QtGui import QStandardItemModel,QColor
from PyQt5.QtCore import Qt,QModelIndex
from image_loader import image

from image_loader.get_line import getLine
from image_loader.locate_point import locatePoint
from image_loader.run_item import runItem

from qgis.utils import iface
from qgis.core import Qgis

import os
import csv
from enum import IntEnum


from PyQt5.QtWidgets import QProgressDialog
#from image_loader.measure_to_point import measureToPoint


class cols(IntEnum):
    run = 0
    chainageCorrection = 1
    offsetCorrection = 2
    load = 3
    imageId = 4
    file = 5
    georeferenced = 6
    startM = 7
    endM = 8


header = ['run',
          'chainage\ncorrection',
          'offset\ncorrection',
          'select',
          'image_id',
          'file',
          ]

startRole = Qt.UserRole+2
endRole = Qt.UserRole+3



class detailsTreeModel(QStandardItemModel):
    
    
    def __init__(self,parent=None):
        super().__init__(0,1,parent=parent)
     #   self.setHorizontalHeaderLabels(['run'])
        self.setHorizontalHeaderLabels(header)
        self.cols = cols
        self.fields = {'folder':''}


  #  def clear(self):
   #     for r in reversed(range(0,self.rowCount())):
     #       self.takeRow(r)
        
        
    def isRun(self,index):
        if index.parent().isValid():
            return False
        return True
    

    def data(self,index,role):
        #yellow if any rows with load==True in run
        if role == Qt.BackgroundColorRole and self.isRun(index):
            for row in range(self.rowCount(index)):
                if self.index(row,cols.load,index).data():
                    return QColor('yellow')
            return QColor('white')            
        return super().data(index,role)

    
#(QgsPointXY,QGSPointXY,QModelIndex)->(float,float)

#nearest feature within startM and endM

    #QgsGeometry, linestringM
    def _getLine(self,start,end):
        gps = self.fields['gps']
        startField = self.fields['startMField']
        endField = self.fields['endMField']
        if gps and startField and endField:
            return getLine(gps,startField,endField,startM=start,endM=end)

                
        
        

    #add or set correction.
   # QgsPointXY,QgsPointXY,QModelIndex
    def addCorrection(self,startPoint,endPoint,index):
        
        
        if self.isRun(index):
            startM = self.index(0,cols.startM,index).data()
            endM = self.index(self.rowCount(index)-1,cols.endM,index).data()#max m in run

       # else:
         #   startM = self.index(index.row(),cols.startM,index.parent()).data()
          #  endM = self.index(index.row(),cols.endM,index.parent()).data()

        print('startM',startM)
        print('endM',endM)

        line = self._getLine(startM,endM)
        #print(line)
        if line:
            
            startMeasure,startOffset = locatePoint(line=line,startM=startM,endM=endM,point=startPoint)
            #def locatePoint(line,startM,endM,point):


            endMeasure,endOffset = locatePoint(line=line,startM=startM,endM=endM,point=endPoint)
            print('startMeas',startMeasure)


            self.setData(self.index(index.row(),cols.chainageCorrection),endMeasure-startMeasure)
            self.setData(self.index(index.row(),cols.offsetCorrection),endOffset-startOffset)


    #images:image[] -> None
    def _addImages(self,images):        
       # print(images[0:5])
        toAdd = {}
        for i in images:#ordered by run
            if i.run in toAdd:
                toAdd[i.run].append(i)
            else:
                toAdd[i.run] = [i]
        for run in toAdd:
            ri = self.runItem(run)
            if not ri:
                ri = self._addRun(run)
            ri.addImages(toAdd[run])
            
   
    def ids(self,runIndex):
        return [self.index(r,cols.imageId,runIndex).data() for r in range(self.rowCount(runIndex))]
      
        
    def valueRange(self,index):
        ids = self.ids(index)
        if ids:
            return (min(ids),max(ids))
        else:
            return (0,0)
        
        
    #remove run if no details in it.
    def _updateRun(self,runItem):
        i = self.indexFromItem(runItem)
        #delete if no rows in run
        if self.rowCount(i) == 0:
            self.invisibleRootItem().removeRow(runItem.row())
        
        
#raster image load file is .txt in csv format.
    def loadFile(self,file,load=False):        
        images = [i for i in image.fromCsv(file)]            
        if os.path.exists(self.fields['folder']):
            image.origonalFiles(images,root = self.fields['folder'])
        self._addImages(images)


    #image[] where load True
    def marked(self,findPoints = False):
        marked = []
        for row in range(self.rowCount()):
            ri = self.item(row,cols.run)
            marked += ri.marked()
        return marked




    def addFolder(self,folder):
        self._addImages([image.image(file=file) for file in getFiles(folder,['.tif'])])
        

    def save(self,file):
    
        with open(file,'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['filePath','runId','imageId','name'])#header
            
           # q = runQuery('select file_path,run,image_id,name,groups,AsText(geom) from details',self.database())

            for r in range(self.rowCount()):
                ri = self.index(r,cols.run)
                
                for row in range(self.rowCount(ri)):
                   
                    p = self.index(row,cols['file_path'],ri).data()
                    #can't convert to relative if on different drive
                    try:
                        p = os.path.relpath(p,file)
                    except:
                        p = self.index(row,cols.file,ri).data()


                    w.writerow([p,
                            ri.data(),
                            self.index(row,cols['image_id'],ri).data(),
                            self.index(row,cols['name'],ri).data()
                            ])


    
    def runItem(self,run):
        for r in range(self.rowCount()):
            i = self.item(r,cols['run'])
            if i.data(Qt.EditRole) == run:
                return i
    
    
    def runIndex(self,run):
        for r in range(self.rowCount()):
            i = self.index(r,cols['run'])
            if i.data(Qt.EditRole) == run:
                return i 
        return QModelIndex()
    
    
    #make alphabetical
    
    def _addRun(self,run,chainageCorrection = 0.0,offsetCorrection = 0.0):
        root = self.invisibleRootItem()
        i = runItem(run)
       
        items = [i, 
        toItem(chainageCorrection),
        toItem(offsetCorrection)
        ]
        
        
        runs = [self.index(r,cols['run']).data() for r in range(self.rowCount())]
        root.insertRow(naturalPos(run,runs),items)
        return i
            
    
    
   # def flags(self,index):
        
    #    if self.indexIsRun(index):
  #          #return Qt.ItemIsSelectable
     #       return super().flags(index) & ~Qt.ItemIsEditable 
        
     #   if index.column()==cols['run']:
       #     return super().flags(index) & ~Qt.ItemIsEditable 

      #  return super().flags(index)
    
    
    def remake(self):
        #   profile = os.path.join(test.testFolder,'remake.prof')
        #   pr = cProfile.Profile()
           #####
       #    pr.enable()  
           
           #    pr.disable()
         #      pr.dump_stats(profile)#compatible with snakeviz
   ##########snakeviz remake.prof
   
   
        gps = self.fields['gps']
        startField = self.fields['startMField']
        endField = self.fields['endMField']
        if gps and startField and endField:

                
            progress = QProgressDialog("Calculating positions...","Cancel", 0, 0)#QObjectwithout parent gets deleted like normal python object
            progress.setMinimumDuration(0)
            progress.setAutoClose(False)
            progress.setWindowModality(Qt.WindowModal)
            images = [i for i in self.marked()]#image[]
            image.remakeImages(images=images,layer = gps,startField=startField,endField = endField,progress = progress,useRectangle = self.fields['useRectangle'])
            progress.close()#close immediatly otherwise haunted by ghostly progressbar
            del progress
        
        else:
            iface.messageBar().pushMessage("Image_loader", "'gps layer,startField and EndField required'", level=Qgis.Info)    
        

        

    def load(self):
      #  progress = QProgressDialog("Loading images...","Cancel", 0, 0,parent=self.parent())#QObjectwithout parent gets deleted like normal python object
      #  progress.setMinimumDuration(0)
        #progress.setWindowModality(Qt.WindowModal)
                
        images = [i for i in self.marked()]#image[]
        print(images)
        #progress.setMaximum(len(images))
        
        for i,im in enumerate(images):
           # if progress.wasCanceled():
           #     return
            im.load()
          #  progress.setValue(i)
        
      #  progress.close()#close immediatly otherwise haunted by ghostly progressbar
      #  progress.deleteLater()
     #   del progress


        
    def indexIsRun(self,index):
        if index.isValid():
            return not index.parent().isValid()
        return False
     
    
    def indexIsDetail(self,index):
        return index.parent().isValid()
        
    

    def dropDetails(self,indexes):
        
        #need to remove rows in reverse order
        toRemove = {}
        for i in indexes:
            if self.indexIsDetail(i):
                runRow= i.parent().row()
                
                if runRow in toRemove:
                    toRemove[runRow].append(i.row())
                else:
                    toRemove[runRow] = [i.row()]
                
        for runRow in toRemove:
            runItem = self.itemFromIndex(self.index(runRow,0))
            for row in reversed(sorted(toRemove[runRow])):
                runItem.removeRow(row)
             #   self.detailCount -= 1
            self._updateRun(runItem)
        
        
        
    # is in order of index rather than imageId. Change?
    def markStarts(self,runIndexes,number=20):
        for runIndex in runIndexes:
            for r in range(min(self.rowCount(runIndex),number)):
                self.setData(self.index(r,cols['load'],runIndex),True)
        
    
        
    #mark all details in run  
    #runs:int[] list of rows
    def markRuns(self,runIndexes,value=True):
        for runIndex in runIndexes:
            for r in range(self.rowCount(runIndex)):
                self.setData(self.index(r,cols['load'],runIndex),value)

        
    #mark all details in run  
    def unMarkRun(self,runIndex):
        for r in range(self.rowCount(runIndex)):
            self.setData(self.index(r,cols['load'],runIndex),False)
        
        
    #mark images from startId<=id<=endId. unmarks rest.
    def markBetween(self,runIndex,startId,endId):
        for r in range(self.rowCount(runIndex)):
            imageId = self.index(r,cols['imageId'],runIndex).data()
            if startId <= imageId and imageId <= endId:
                self.setData(self.index(r,cols['load'],runIndex),True)
            else:
                self.setData(self.index(r,cols['load'],runIndex),False)
        
        
        

def clamp(n,minimum,maximum):
    if n < minimum:
        return minimum
    
    if n > maximum:
        return maximum
    
    return n


def getFiles(folder,exts=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            if os.path.splitext(f)[1] in exts or exts is None:
                yield os.path.join(root,f)





import re

def naturalSort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)



def naturalPos(item,items):
    s = naturalSort(items +[item])
    return s.index(item)

from PyQt5.QtGui import QStandardItem


def toItem(data):
    i = QStandardItem()
    i.setData(data,Qt.EditRole)
    return i

