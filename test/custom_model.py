# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 13:56:09 2023

@author: Drew.Bennett
"""

class image:
    
    #run:str
    def __init__(self,imageId = None,file='',georeferenced='',run = '',startM = 0.0,endM = 0.0,offset = 0.0):
        
        self.georeferenced = str(georeferenced)
        self.file = str(file)
        self.run = run
     


class run:
    
    def __init__(self,name):
        self.images = []#image[]
        self.name = name
        
        
        
        
from PyQt5.QtCore import Qt



from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QAbstractItemModel


    
    
class runModel(QAbstractItemModel):
     
     
    def __init__(self,parent=None):
        super().__init__(parent)
        self.runs = []
         
         
         
    def addRun(self,name):
        if not name in self.runs:
            self.runs.append(run(name=name))
        
    
    def findRun(self,name):
        for run in self.runs:
            if run.name == name:
                return run
    
    
    def addImages(self,images):
        for i in images:
            self.addRun(i.run)
            self.findRun(i.run).images.append(i)
            
    
    def data(self,index,role=Qt.EditRole):
        return 'data'
         
    
    def rowCount(self,parent = QModelIndex()):
        return len(self.runs)
    
    
    def columnCount(self,parent = QModelIndex()):
        return 10
    
    
    
    def index(self,row,column,parent=QModelIndex()):
        
        index = QModelIndex()
        
        if row < len(self.runs):
            if column ==0 :
                index.setData(self.runs[row].name)
            
        
        return index
    
    
from PyQt5.QtWidgets import QTreeView


m = runModel()    

i = image()

m.addImages([i])
v = QTreeView()
v.setModel(m)
v.show()


