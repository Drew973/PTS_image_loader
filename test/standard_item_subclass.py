# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 09:49:56 2023

@author: Drew.Bennett
"""





from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtWidgets import QTreeView

from PyQt5.QtCore import Qt


class image(QStandardItem):
    
    
    def __init__(self,parent=None):
        super().__init__()        
        
        self.idItem = QStandardItem()
        self.fileItem = QStandardItem()
        self.fileItem.setData('filename',Qt.EditRole)
        
        #self.setChild(0,1,self.idItem)
        self.appendRow([self.idItem,self.fileItem])
        
       # self.imageId = -1
        self.imageId = -1
        
        self.setData('image item',Qt.EditRole)
        
        
    @property
    def imageId(self):
        return self.idItem.data(Qt.EditRole)
        
    
    @imageId.setter
    def imageId(self,value):
      #  print('id set',value)
        self.idItem.setData(value,Qt.EditRole)
    
    
    def items(self):
       # print('id data',self.idItem.data(Qt.EditRole))#None
        #item = QStandardItem('item data')
        
        item = QStandardItem()
        item.setData(self.imageId,Qt.EditRole)
        
        #item.setData()
        return [item]
    
    
    #self<other
    def __lt__(self,other):
        return self.imageId<other.imageId
       
        
    def __eq__(self,other):
        return self.imageId == other.imageId
    


    #sortChildren
    
class run(QStandardItem):
    
    def __init__(self,name = '',parent=None):
        super().__init__()        
        self.setData(name,Qt.EditRole)
        
    
    #add images in order
    def addImages(self,images):
        a = sorted(images+self.images())
        
        print(a)
        for i in reversed(sorted(images)):
            r = a.index(i)
            print(r)
           # self.insertRow(r,i.items())
            self.appendRow(i.items())

        
  #  def ids(self):
  #      return [self.item(row,cols.imageId).data(Qt.EditRole) for row in range(self.rowCount)]
        
    #->image[]
    def images(self):
        return [self.image(r) for r in range(self.rowCount())]
    
    
    def image(self,row):
        pass
   
   
    @classmethod
    #QStandardItem[]
    def items(cls,image):
        return [QStandardItem('')]
    
    
        
   # def child(self,row,column):
     #   self.images    

    
    
i = image()
i.imageId = 10

print(i.idItem.data(Qt.EditRole))

print(i.imageId)

i2 = image()
i2.imageId = 2

#print(i.imageId)
    
m = QStandardItemModel(0,5)
runItem = run(name='run name')
m.appendRow(runItem)
runItem.addImages([i,i2])

v = QTreeView()
v.setModel(m)
v.show()
        
