# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 10:05:27 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QDialog,QFormLayout
from qgis.core import QgsMapLayerProxyModel,QgsFieldProxyModel
from qgis.gui import QgsMapLayerComboBox,QgsFieldComboBox



class setLayersDialog(QDialog):
        
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLayout(QFormLayout(self))
        self.layerWidget = QgsMapLayerComboBox(self)
        self.layerWidget.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.layout().addRow('Layer with frames',self.layerWidget)
        
        self.idBox = QgsFieldComboBox(self)
        self.idBox.setFilters(QgsFieldProxyModel.Int|QgsFieldProxyModel.String)
        self.layerWidget.layerChanged.connect(self.layerSet)
        self.idBox.setLayer(self.layerWidget.currentLayer())
        self.layout().addRow('Field with id',self.idBox)
      
    def layerSet(self,layer):
        self.idBox.setLayer(layer)
        
    def framesLayer(self):
        return self.layerWidget.currentLayer()
    
    def idField(self):
        return self.idBox.currentField ()
        
    
def test():
    d = setLayersDialog()
    d.show()
    return d
    
    
if __name__=='__console__':
    d = test()
    
    
    