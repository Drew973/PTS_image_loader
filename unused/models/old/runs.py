# -*- coding: utf-8 -*-
"""
Created on Fri Jan 27 08:35:41 2023

@author: Drew.Bennett
"""


from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtCore import Qt




runCols = {'run':0,
           'load':1,
           'start_id':2,
           'end_id':3,
           'max_id':4,
           'min_id':5}




class runsModel(QStandardItemModel):
    
    
    def __init__(self,parent=None):
        super().__init__(0,len(runCols),parent=parent)
        self.setHorizontalHeaderLabels([k for k in runCols])

       
    def fieldIndex(self,name):
        if name in runCols:
            return runCols[name]
        return -1
    
            
    def _addRun(self,run,minId,maxId):
        items = [toItem(run),toItem(False),toItem(minId),toItem(maxId),toItem(maxId),toItem(minId)]
        self.invisibleRootItem().appendRow(items)
    
    
 
    def update(self,runs,imageModel):
        for run in runs:
            self.updateRun(run,imageModel)
 
    
    #row with run .int or None  
    def findRun(self,run):
        for row in range(self.rowCount()):
            if self.index(row,runCols['run']).data() == run:
                return row
    
    
    
    def minValue(self,index):
        return self.index(index.row(),runCols['min_id']).data()
        
    
    def maxValue(self,index):
        return self.index(index.row(),runCols['max_id']).data()

        
    
    def flags(self,index):
        if index.column()==self.fieldIndex('load'):
            return super().flags(index) | Qt.ItemIsUserCheckable# | Qt.ItemIsEditable
        
        if index.column() in [self.fieldIndex('start_id'),self.fieldIndex('end_id')]:
            return super().flags(index)
        
        return super().flags(index) & ~Qt.ItemIsEditable

    
    
    def updateRun(self,run,imageModel):
                
        ids = imageModel.ids(run)
        row = self.findRun(run)

        if ids:
            minId = min(ids)
            maxId = max(ids)
            
            #add new run if doesn't exist
            if row is None:
                self._addRun(run,minId,maxId)
                return
            

            
            #update min_id
            i = self.index(row,runCols['min_id'])
            if i.data() != minId:
                self.setData(i,minId)
    
            #update max_id
            i = self.index(row,runCols['max_id'])
            if i.data() != maxId:
                self.setData(i,maxId)
    
    
            self._clamp(self.index(row,runCols['start_id']),minId,maxId)
            self._clamp(self.index(row,runCols['end_id']),minId,maxId)

            
        #remove if no ids left in run.
        else:
            self.takeRow(row)
        
    #set data at index if not mimimum<=data<=maximum
    def _clamp(self,index,minimum,maximum):
        d = index.data()
        c = clamp(d,minimum,maximum)
        if c!=d:
            self.setData(index,c)
    

def clamp(n,minimum,maximum):
    if n < minimum:
        return minimum
    
    if n > maximum:
        return maximum
    
    return n

def toItem(data):
    i = QStandardItem()
    i.setData(data,Qt.EditRole)
    return i