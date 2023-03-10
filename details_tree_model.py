# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 12:00:08 2023

@author: Drew.Bennett


tree model to store details and run info


markBetween dialog.
    startId,
    endId,


"""





from PyQt5.QtGui import QStandardItemModel,QStandardItem,QColor
from PyQt5.QtCore import Qt
from qgis.core import QgsProject,QgsLayerTreeGroup,Qgis
from qgis.utils import iface
#from models.details import image_details

from image_loader import generate_details
from image_loader import load_image
from image_loader import image


import os
import csv
import json

from enum import IntEnum



class cols(IntEnum):
    run = 0
    chainageCorrection = 1
    offsetCorrection = 2
    
    load = 3
    imageId = 4
    name = 5
    file = 6
    georeferenced = 7
    groups = 8



header = ['run',
          'chainage\ncorrection',
          'offset\ncorrection',
          'select',
          'image_id',
          'name',
          'file',
          'georeferenced\nfile',
          'groups']


startRole = Qt.UserRole+2
endRole = Qt.UserRole+3



class run:
    def __init__(self,name='',images = [],chainageCorrection=0,offsetCorrection = 0):
        self.name = name
        self.images = images
        self.chainageCorrection = chainageCorrection
        self.offsetCorrection = offsetCorrection
        
        
        

class detailsTreeModel(QStandardItemModel):
    
    
    def __init__(self,parent=None):
        super().__init__(0,1,parent=parent)
     #   self.setHorizontalHeaderLabels(['run'])
        self.clear()
     

    def clear(self):
        self.setHorizontalHeaderLabels(header)
        #for r in range(self.rowCount()):
         #   self.takeRow(r)
        
        
        
        
    def isRun(self,index):
        if index.parent().isValid():
            return False
        return True
    

    def data(self,index,role):
        #yellow if any rows with load==True in run
       # if role == Qt.BackgroundColorRole and self.isRun(index):
         #   for row in range(self.rowCount(index)):
       #         if self.index(row,cols.load,index).data():
         #           return QColor('yellow')
         #   return QColor('white')    
        
        
       # if not index.parent().isValid():#run
        #    if role == Qt.DisplayRole:
       #         if index.column() == 0:
        #            return 'run:'+str(index.data(Qt.EditRole))
        
        return super().data(index,role)

    #toDo: order by imageId
    def addDetail(self,run='',name='',imageId = None,load=False,filepath='',groupsString=''):
        
        if not run:
            run = generate_details.generateRun(filepath)
        
        if imageId is None:
            imageId = generate_details.generateImageId(filepath)

            
        if not name:
             name = '{run}_{imageId}'.format(run=run,imageId=imageId)
        
        if not groupsString:
            groupsString = generate_details.generateGroups(run=run,imagetype = generate_details.generateType(filepath))
        
        ri = self.runItem(run)
        if ri is None:
            ri = self._addRun(run)
        
        runIndex = self.indexFromItem(ri)
        ids = sorted(self.ids(runIndex)+[imageId])
        pos = ids.index(imageId)
        
        
        items = [None]*len(cols)
        items[cols.run] = toItem('')
        items[cols.imageId] = toItem(imageId)
        items[cols.load] = toItem(load)
        items[cols.name] = toItem(name)
        items[cols.file] = toItem(filepath)
        items[cols.groups] = toItem(groupsString)
        
        ri.insertRow(pos,items)#ordered by run id
        
     #   self.detailCount += 1
    
    #images:image[] -> None
    def addImages(self,images):
        images = sorted(images) #sorted by run,id,file...
        
        runs = {} #{run:[image[]}
        
        for i in images:
            if i.run in images:
                runs[i.run].append(i)
            else:
                runs[i.run] = [i]
                
        
        for run in runs:
            ri = self.runItem(run)
            if ri is None:
                ri = self._addRun(run)
            
            runIndex = self.indexFromItem(ri)

            ids  = self.ids(runIndex)
            
           # for i in runs[run]:
            #    se
            
    #i:image
    def addImage(self,i,runIndex,row):
        
        items = [None]*len(cols)
        items[cols.run] = toItem('')
        items[cols.imageId] = toItem(i.imageId)
        items[cols.load] = toItem(False)
        items[cols.name] = toItem(i.name)
        items[cols.file] = toItem(i.filepath)
        items[cols.groups] = toItem(i.groupsString)
        
       # ri.insertRow(pos,items)#ordered by run id
    
    
    
    def ids(self,runIndex):
        idCol = cols.imageId
        return [self.index(r,idCol,runIndex).data() for r in range(self.rowCount(runIndex))]
      
        
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
        ext = os.path.splitext(file)[-1]
        if ext in ['.csv','.txt']:
          #  self.addDetails([d for d in image_details.fromCsv(file)])

            images = []
            with open(file,'r',encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.lower().replace('_','') for name in reader.fieldnames]#lower case keys/fieldnames                 
                for d in reader:
                    
                    p = d['filepath']
                    if os.path.isabs(p):
                        filePath = p
                    else:
                        filePath = os.path.normpath(os.path.join(file,p))#from file not folder
                    
                    
                    #try to convert imageId to int
                    try:
                        imageId = find(d,'imageid')
                        if imageId is not None:
                            imageId = int(imageId)
                            
                    except Exception as e:
                        print(e)
                        imageId = None
                    
                    
                   # images.append(image(filepath = filePath,
                        #           run = find(d,'runid'),
                    #               imageId = imageId,
                       #            name = find(d,'name'),
                      #             groupsString = find(d,'groups'),
                      #             ))
                    
                    
                    self.addDetail(filepath = filePath,
                                   run = find(d,'runid'),
                                   imageId = imageId,
                                   name = find(d,'name'),
                                   groupsString = find(d,'groups'),
                                   load=load)
                    


    #count all images where load is True
    def loadCount(self):
        total = 0
        for r in range(self.rowCount()):
            ri = self.index(r,cols.run)
            for r2 in range(self.rowCount(ri)):
                if self.index(r2,cols.load,ri).data() == True:
                    total+=1
        return total



    
    def loadImages(self,progress):
     #   import time   #################
        
        #remove all items from image_loader group
        for c in QgsProject.instance().layerTreeRoot().children():
            if c.name() == 'image_loader' and isinstance(c,QgsLayerTreeGroup):
                c.removeAllChildren()
        
     
     #   progress.setMaximum(self.detailCount)
        progress.setMaximum(self.loadCount())
       # print('maximum:',progress.maximum())
        
        total = 0
        unfound = []
     #   load_image.removeChild('image_loader')#remove group


       # imageLoaderGroup = QgsProject.instance().layerTreeRoot().addGroup('image_loader')

        for r in range(self.rowCount()):
            ri = self.index(r,cols.run)
          #  group = parent.addGroup(ri.data())
            for r2 in range(self.rowCount(ri)):
               
                if progress.wasCanceled():
                    return
                
                if self.index(r2,cols.load,ri).data() == True:
                    #default groups to ['image_loader'] if not valid JSON
                    try:
                        groups = json.loads(self.index(r2,cols.groups,ri).data())
                    except:
                        groups = ['image_loader']
                    
                    filePath = self.index(r2,cols.file,ri).data()
                    if os.path.exists(filePath):
                        load_image.loadImage(filepath = filePath,
                                  name = self.index(r2,cols.name,ri).data(),
                                  groups = groups)
                        
                    else:
                        unfound.append(filePath)
                    total += 1
                    progress.setValue(total)######slow
                    
        if unfound:
            iface.messageBar().pushMessage("image loader failed to find: "+'\n'.join(unfound), level=Qgis.Info)

                    

    def addFolder(self,folder):
        for i in generate_details.getImages(folder):
            #print(i)
            self.addDetail(filepath=i)


    def save(self,file):
        print('detailsTreeModel.save',file)
       

    
        with open(file,'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['filePath','runId','imageId','name','groups'])#header
            
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
                            self.index(row,cols['name'],ri).data(),
                            self.index(row,cols['groups'],ri).data()
                            ])


    
    def runItem(self,run):
        
        for r in range(self.rowCount()):
            i = self.item(r,0)
            if i.data(Qt.EditRole) == run:
                return i
    
    
    #make alphabetical
    
    def _addRun(self,run):
        root = self.invisibleRootItem()
        i = QStandardItem()
        i.setData(run,Qt.EditRole)
        runs = [self.index(r,cols['run']).data() for r in range(self.rowCount())]
        root.insertRow(naturalPos(run,runs),i)
        return i
            
    
    
    def flags(self,index):
        
        if self.indexIsRun(index):
            #return Qt.ItemIsSelectable
            return super().flags(index) & ~Qt.ItemIsEditable 
        
        if index.column()==cols['run']:
            return super().flags(index) & ~Qt.ItemIsEditable 

        return super().flags(index)
    
    
        
        
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
        
        
        
        
      #mark all details in run  
    def markRun(self,runIndex):
        for r in range(self.rowCount(runIndex)):
            self.setData(self.index(r,cols['load'],runIndex),True)

        
      #mark all details in run  
    def unMarkRun(self,runIndex):
        for r in range(self.rowCount(runIndex)):
            self.setData(self.index(r,cols['load'],runIndex),False)
        
        
        
    def markBetween(self,runIndex,startId,endId):
        for r in range(self.rowCount(runIndex)):
            imageId = self.index(r,cols['image_id'],runIndex).data()
            if startId <= imageId and imageId <= endId:
                self.setData(self.index(r,cols['load'],runIndex),True)
        
        
        
        
def toItem(data):
    i = QStandardItem()
    i.setData(data,Qt.EditRole)
    return i


def clamp(n,minimum,maximum):
    if n < minimum:
        return minimum
    
    if n > maximum:
        return maximum
    
    return n


 #lookup value from dict, returning default if not present
def find(d,k,default=None):
    if k in d:
        return d[k]
    return default


import re

def naturalSort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)



def naturalPos(item,items):
    s = naturalSort(items +[item])
    return s.index(item)


#runs = ['a1a','2','12','3','4','5','6','7','8','8','9','10','11a']
#print(naturalPos('6',runs))
