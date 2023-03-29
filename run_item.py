# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 15:20:35 2023

@author: Drew.Bennett
"""




from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import Qt
from image_loader import image

from enum import IntEnum


class imageCols(IntEnum):
    run = 0
    chainageCorrection = 1
    offsetCorrection = 2
    
    load = 3
    imageId = 4
    file = 5
    georeferenced = 6




class runItem(QStandardItem):
    
    def __init__(self,name = ''):
        super().__init__(0,len(imageCols))        
        self.setData(name,Qt.EditRole)
        
    
    #add images in order
    def addImages(self,images):
        a = sorted(images+self.images())
        self.removeRows(0,self.rowCount())#remove all rows
        for i in sorted(a):
            self.appendRow(self.itemsFromImage(i))


    def images(self):
        return [self.imageFromRow(row) for row in range(self.rowCount())]
            


    def imageFromRow(self,row):
        role = Qt.EditRole
        return image.image(
        run = self.data(Qt.EditRole),
        imageId = self.child(row,imageCols.imageId).data(role),
        file = self.child(row,imageCols.file).data(role),
        georeferenced = self.child(row,imageCols.georeferenced).data(role)
        )
        

    @classmethod
        #image -> QStandardItem[]
    def itemsFromImage(cls,image):
        items = [toItem('')]*len(imageCols)
        items[imageCols.load] = toItem(False)
        items[imageCols.imageId] = toItem(image.imageId)
        items[imageCols.file] = toItem(image.file)
        items[imageCols.georeferenced] = toItem(image.georeferenced)
        return items
           
    
    
    
    
    def marked(self):
        chainageCorrection = self.index().model().index(self.index().row(),imageCols.chainageCorrection).data()
        offsetCorrection = self.index().model().index(self.index().row(),imageCols.offsetCorrection).data()
            
        images = []
        for row in range(self.rowCount()):
            if self.child(row,imageCols.load).data(Qt.EditRole) ==True:
                im = self.imageFromRow(row)
                im.startM = (im.imageId * 5 + chainageCorrection)/1000 ###want correction in km
                im.endM = im.startM+0.005 # 5m later
                im.offset = offsetCorrection
                images.append(im)
                
                
        return images
        
        
    
def toItem(data):
    i = QStandardItem()
    i.setData(data,Qt.EditRole)
    return i
    
    