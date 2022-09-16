# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 10:05:27 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QDialog,QFormLayout
from qgis.core import QgsMapLayerProxyModel,QgsFieldProxyModel
from qgis.gui import QgsMapLayerComboBox

from image_loader.widgets.field_box import fieldBox


class setLayersDialog(QDialog):
        
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLayout(QFormLayout(self))
        self.layerWidget = QgsMapLayerComboBox(self)
        self.layerWidget.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.layout().addRow('Layer with frames',self.layerWidget)
        
        self.idBox = fieldBox(parent = self.layerWidget,default = 'sectionID')
        self.idBox.setFilters(QgsFieldProxyModel.Int|QgsFieldProxyModel.String)
        self.layout().addRow('Field with id',self.idBox)
      
        self.runBox = fieldBox(parent = self.layerWidget,default = 'run')
        self.runBox.setFilters(QgsFieldProxyModel.String)
        self.layout().addRow('Field with run',self.runBox)
        
        

    def framesLayer(self):
        return self.layerWidget.currentLayer()
    
    
    def idField(self):
        return self.idBox.currentField()

        
    def runField(self):
        return self.runBox.currentField()

    
    def fields(self):
        return {'framesLayer':self.layerWidget.currentLayer(),'idField':self.idBox.currentField(),'runField':self.runBox.currentField()}


    #dict like.
    def __getitem__ (self,key):
        return self.fields()[key]
        
        
def test():
    d = setLayersDialog()
    d.show()
    return d
    
    
if __name__=='__console__':
    d = test()
    
    
    