# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 15:51:51 2023

@author: Drew.Bennett



QSqLTable model buggy and causing crashes?




detailsModel:
    contains runsModel.


    addDetail:
        adds detail and updates runs
   
    removeRow():
        removes row and updates rund
    
    
    
    

    runs model:
    



"""



from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtCore import Qt

#from . import runs
from image_loader.models.details import image_details
import os
from qgis.utils import iface
from qgis.core import Qgis
import csv

from PyQt5.QtCore import pyqtSignal
from image_loader.functions import group_functions



detailCols = {'run':0,
              'load':1,
               'image_id':2,
               'file_path':3,
               'name':4,
               'groups':5}




class detailsModel(QStandardItemModel):
    runsChanged = pyqtSignal(list)

    def __init__(self,parent=None):
        super().__init__(0,0,parent=parent)
        self.setHorizontalHeaderLabels([k for k in detailCols])
        #self.runsModel = runs.runsModel()
        self.runsModel = None
        
       
        
    def clear(self):
        runs = []
        for r in range(self.rowCount()):
            run = self.index(r,detailCols['run']).data()
            if not run in runs:
                runs.append(run)
        super().clear()
        self.setHorizontalHeaderLabels([k for k in detailCols])#clear() removes header labels
        self.runsChanged.emit(runs)


    def fieldIndex(self,name):
        if name in detailCols:
            return detailCols[name]
        return -1
    
    
    def flags(self,index):
        if index.column()==self.fieldIndex('load'):
            return super().flags(index) | Qt.ItemIsUserCheckable# | Qt.ItemIsEditable
        
      #  if index.column() in [self.fieldIndex('image_id'),self.fieldIndex('end_id')]:
          #  return super().flags(index)
        
        return super().flags(index) & ~Qt.ItemIsEditable

    
    def _addDetail(self,run,imageId,filePath='',name='',groups=''):
        items = [toItem(run),toItem(False),toItem(imageId),toItem(filePath),toItem(name),toItem(groups)]
        self.invisibleRootItem().appendRow(items)
    
    
    def addDetails(self,details):
        runs = []

        for d in details:
            self._addDetail(d['run'],d['imageId'],d['filePath'],d['name'],d['groupsString'])
            if not d['run'] in runs:
                runs.append(d['run'])
        
      #  if not self.runsModel is None:
         #   self.runsModel.update(runs=runs,imageModel=self)
        self.runsChanged.emit(runs)
    
    
    
    #list of rows
    def dropRows(self,rows):
        runs = []
        
        for row in sorted(rows,reverse=True):
            run = self.takeRow(row)[detailCols['run']].data(Qt.EditRole)
            if not run in runs:
                runs.append(run)
                
      #  if not self.runsModel is None:
      #      self.runsModel.update(runs=runs,imageModel=self)
        self.runsChanged.emit(runs)
        
    
    #return list of ids in run
    def ids(self,run):
        ids = []
        for r in range(self.rowCount()):
            if self.index(r,detailCols['run']).data() == run:
                ids.append(self.index(r,detailCols['image_id']).data())
        return ids
    
    
    
    def setLayers(self,fields):
        pass
    
    
#progress is QProgressDialog
#finding extents is slow. other details is not.
    def addFolder(self,folder,progress=None):
        files = [f for f in image_details.getFiles(folder,['.tif'])]
        self.addDetails([image_details.imageDetails(f) for f in files])    



    #load iterable of details and maybe display cancellable progress bar.
   #QgsTask is very buggy. QProgressDialog much simpler.
    def loadDetails(self,progress):
        
        group_functions.removeChild('image_loader')#remove group

        progress.setMaximum(self.rowCount())
        fileCol = detailCols['file_path']
        runCol = detailCols['run']
        idCol = detailCols['image_id']
        nameCol = detailCols['name']
        groupsCol = detailCols['groups']
        loadCol = detailCols['load']
        
        for r in range(self.rowCount()):
            if self.index(r,loadCol).data():
            
            #filePath,run=None,imageId=None,name=None,groups=None
                d = image_details.imageDetails(filePath = self.index(r,fileCol).data(),
                                               run = self.index(r,runCol).data(),
                                               imageId = self.index(r,idCol).data(),
                                               name = self.index(r,nameCol).data(),
                                               groups = self.index(r,groupsCol).data())
            
                d.load()
                
    
                progress.setValue(r)
                if progress.wasCanceled():
                    break

    
    
    #write csv/txt, converting file_paths to relative if possible
    def saveAsCsv(self,file):
               
        with open(file,'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['filePath','runId','imageId','name','groups'])#header
            
           # q = runQuery('select file_path,run,image_id,name,groups,AsText(geom) from details',self.database())


            for row in range(self.rowCount()):
                
                p = self.index(row,detailCols['path']).data()
                #can't convert to relative if on different drive
                try:
                    p = os.path.relpath(p,file)
                except:
                    p = self.index(row,detailCols['path']).data()
            
            
                w.writerow([p,
                            self.index(row,detailCols['run']).data(),
                            self.index(row,detailCols['image_id']).data(),
                            self.index(row,detailCols['name']).data(),
                            self.index(row,detailCols['groups']).data(),
                           # self.index(row,detailCols['groups']).data(),
                            ])
                
        iface.messageBar().pushMessage("Image_loader", "Saved to csv", level=Qgis.Info)
        
        
    
    
#raster image load file is .txt in csv format.
    def loadFile(self,file):        
        ext = os.path.splitext(file)[-1]
        if ext in ['.csv','.txt']:
            self.addDetails([d for d in image_details.fromCsv(file)])
            return True
        iface.messageBar().pushMessage('{ext} file format not supported.'.format(ext=ext), level=Qgis.Critical) 
        return False
    
    
    
    
def toItem(data):
    i = QStandardItem()
    i.setData(data,Qt.EditRole)
    return i



class testRunsModel(QStandardItemModel):
    
    def printRuns(self,runs):
        print(runs)
    
    
def test():
    from PyQt5.QtWidgets import QTableView    
    m = detailsModel()
    
    m2 = testRunsModel()
    
    m.runsChanged.connect(m2.printRuns)
    m._addDetail(run = 'a',imageId = 3)
    m._addDetail(run = 'a',imageId = 4)
    m._addDetail(run = 'a',imageId = 5)
    
    m2 = testRunsModel()

    v = QTableView()
    #v = QTreeView()
    v.setModel(m)
    
    v.show()
    
    m = detailsModel()
    m._addDetail(run = 'a',imageId = 3)
    m._addDetail(run = 'a',imageId = 4)
    m._addDetail(run = 'a',imageId = 5)
    v.setModel(m)

    return v

if __name__=='__console__':
    v = test()


