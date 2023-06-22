# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 10:05:27 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit,QCheckBox

from qgis.core import QgsMapLayerProxyModel,QgsFieldProxyModel
from qgis.gui import QgsMapLayerComboBox

from image_loader.widgets.field_box import fieldBox


class setLayersDialog(QDialog):
        
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLayout(QFormLayout(self))
      #  self.layerWidget = QgsMapLayerComboBox(self)
      #  self.layerWidget.setFilters(QgsMapLayerProxyModel.PolygonLayer)
      #  self.layout().addRow('Layer with frames',self.layerWidget)
        
      #  self.idBox = fieldBox(parent = self.layerWidget,default = 'sectionID')
     #   self.idBox.setFilters(QgsFieldProxyModel.Int|QgsFieldProxyModel.String)
      #  self.layout().addRow('Field with id',self.idBox)
      
       # self.runBox = fieldBox(parent = self.layerWidget,default = 'run')
        #self.runBox.setFilters(QgsFieldProxyModel.String)
       # self.layout().addRow('Field with run',self.runBox)
        
        
     #   self.gpsLayerBox = QgsMapLayerComboBox(self)
     #   self.gpsLayerBox.setFilters(QgsMapLayerProxyModel.LineLayer)
     #   self.layout().addRow('Layer with gps lines',self.gpsLayerBox)
        
     #   self.startMBox = fieldBox(parent = self.gpsLayerBox,default = 'startM')
     #   self.startMBox.setFilters(QgsFieldProxyModel.Numeric)
     #   self.layout().addRow('Field with start m values',self.startMBox)        
        
        #self.endMBox = fieldBox(parent = self.gpsLayerBox,default = 'endM')
      #  self.endMBox.setFilters(QgsFieldProxyModel.Numeric)
     #   self.layout().addRow('Field with end m values',self.endMBox)      
        
        
        self.folder = QLineEdit()
       # self.folder.setText(r'D:\RAF Shawbury')####################################remove before release
        self.layout().addRow('Project folder',self.folder)
        
      #  self.useRectangle = QCheckBox()
     #   self.useRectangle.setChecked(True)
       # self.layout().addRow('Treat images as rectangle',self.useRectangle)      

        

    def framesLayer(self):
        return self.layerWidget.currentLayer()
    
    
    def idField(self):
        return self.idBox.currentField()

        
    def runField(self):
        return self.runBox.currentField()

    
    def fields(self):
        return {
               # 'framesLayer':self.layerWidget.currentLayer(),
             #   'idField':self.idBox.currentField(),
                'folder':self.folder.text(),
          #      'gps':self.gpsLayerBox.currentLayer(),
           #     'startMField':self.startMBox.currentField(),
           #     'endMField':self.endMBox.currentField(),
           #     'useRectangle':self.useRectangle.isChecked()
                }


    #dict like.
    def __getitem__ (self,key):
        return self.fields()[key]
        
        
def test():
    d = setLayersDialog()
    d.show()
    return d
    
    
if __name__=='__console__':
    d = test()
    
    
    