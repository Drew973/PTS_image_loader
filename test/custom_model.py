# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 13:56:09 2023

@author: Drew.Bennett
"""





class run:
    
    def __init__(self,name):
        self.images = []#image[]
        self.name = name
        
        
        
from PyQt5.QtCore import Qt
from image_loader.image import image



from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QAbstractItemModel


    
    
class runModel(QAbstractItemModel):
     
     
    def __init__(self,parent=None):
        super().__init__(parent)
        self.runs = {}
         
         
         
    def addRun(self,name):
        if not name in self.runs:
            self.runs[name] = run(name)
        
    
    
    def addImages(self,images):
        for i in images:
            self.addRun(i.run)
            self.runs[i.run].images.append(i)
            
    
    def data(self,index,role=Qt.EditRole):
        return 'data'
         
    
    def rowCount(self,parent = QModelIndex()):
        return len(self.runs)
    
    
    def columnCount(self,parent = QModelIndex()):
        return 10
    
    
from PyQt5.QtWidgets import QTreeView


m = runModel()    

i = image()

m.addImages([i])
v = QTreeView()
v.setModel(m)
v.show()


