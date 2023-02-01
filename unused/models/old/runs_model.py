# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 09:58:55 2023

@author: Drew.Bennett




QProxyModel
"""


from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtCore import Qt



columns = {'run':0,
           'show':1,
           'start_id':2,
           'end_id':3,
           'max_id':4,
           'min_id':5}


class runsModel(QStandardItemModel):
    
    
    def __init__(self,parent=None):
        super().__init__(0,len(columns),parent=parent)
        
        for k in columns:
            self.setHeaderData(columns[k],Qt.Horizontal,k)
        
        
        
    def runs(self):
        col = columns['run']
        return [self.index(r,col).data() for r in range(self.rowCount())]
        
        
    #update after details added to imageModel
    def detailsAdded(self,details,imageModel):
        
        existing = self.runs()
        
        runs = []
        
        for d in details:
            if not d['run'] in runs:
                runs.append(d['run'])
        
        
        for r in runs:
            if not r in existing:
                self.appendRow([toItem(r),toItem(False)])
            
            self.updateRun(r,imageModel)
        
        
        
    def updateRun(self,run,imageModel):
        
        pass
       # s,e = imageModel.minMax(run)
        
        
        
    #update after details removed from imageModel
    def detailsRemoved(self,details):
        pass
        #if details 


    def fieldIndex(self,label):
        return columns[label]
    
    
def toItem(data):
    i = QStandardItem()
    i.setData(data)
    return i