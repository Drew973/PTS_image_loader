# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 10:45:45 2023

@author: Drew.Bennett
"""

from image_loader.point_widget import pointWidget

from PyQt5.QtWidgets import QDialog,QFormLayout,QDialogButtonBox
from qgis.core import QgsCoordinateReferenceSystem
from PyQt5.QtCore import QModelIndex


class correctionsDialog(QDialog):
    
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLayout(QFormLayout())
            
        
        crs = QgsCoordinateReferenceSystem('EPSG:27700')
        
        self.startWidget = pointWidget(parent=self,crs = crs)
        self.layout().addWidget(self.startWidget)
        self.layout().addRow('Current position',self.startWidget)
        
        self.endWidget = pointWidget(parent=self,crs = crs)
        self.layout().addRow('Desired position',self.endWidget)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,parent=self)
        self.layout().addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setIndex(QModelIndex())


    def setIndex(self,index):
        self.index = index


    def accept(self):
        
        if self.index.isValid():
            model = self.index.model()
            model.addCorrection(startPoint=self.startWidget.point,endPoint=self.endWidget.point,index=self.index)
        
        super().accept()

def test():
    
    #crs = QgsCoordinateReferenceSystem('EPSG:27700')
   # w = pointWidget(crs=crs)
   
    d = correctionsDialog()
    d.show()
    return d

if __name__ == '__console__':
    w = test()