# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 12:49:18 2025

@author: Drew.Bennett
"""


from qgis.gui import QgsMapLayerComboBox , QgsFieldComboBox
from qgis.core import QgsFieldProxyModel,Qgis
from PyQt5.QtWidgets import QDialog,QFormLayout,QDialogButtonBox,QSpinBox
from image_loader import settings,backend,file_locations
from image_loader.type_conversions import asInt
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl



def openHelp():
   # url.setFragment('#runs from layer')#windows ignores fragment.
    QtGui.QDesktopServices.openUrl(QUrl(file_locations.runsFromLayerHelp))


class runsFromAreasDialog(QDialog):
    
    def __init__(self , runsModel , parent=None):
        super().__init__(parent)
        self.setWindowTitle('Image loader: runs from polygon Layer')
        self.setLayout(QFormLayout(self))
        self.layerBox = QgsMapLayerComboBox()
        self.layerBox.setFilters(Qgis.LayerFilter.PolygonLayer)
        self.layout().addRow('Layer',self.layerBox)        
        self.bearing = QgsFieldComboBox()
        self.bearing.setAllowEmptyFieldName(True)
        self.layerBox.layerChanged.connect(self.bearing.setLayer)
        self.bearing.setLayer(self.layerBox.currentLayer())
        self.bearing.setFilters(QgsFieldProxyModel.Numeric)
        self.bearing.setToolTip('Optional. Field with direction.')
        self.layout().addRow('Bearing Field',self.bearing)
        self.angle = QSpinBox()
        self.angle.setValue(asInt(settings.value('maxAngle'),25))
        self.angle.setMaximum(90)
        self.angle.setToolTip('Ignore where angle between vehicle bearing and bearing field > this')
        self.layout().addRow('Maximum angle(degrees)',self.angle)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel|QDialogButtonBox.Help)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        buttons.helpRequested.connect(openHelp)
        self.layout().addWidget(buttons)
        self.runsModel = runsModel
    
    
    def accept(self):
         settings.setValue('maxAngle',self.angle.value())
         layer = self.layerBox.currentLayer()
         bearingField = self.bearing.currentField()
         if layer is not None:
             runData = backend.runs_functions.runsFromAreas(features = layer.getFeatures() ,
                                                            crs = layer.crs() ,
                                                            bearingField = bearingField,
                                                            maxAngle = self.angle.value())
     #    print('runData',runData)
         backend.runs_functions.insertRuns(runData)
         return super().accept()


if __name__ =='__console__':
    d = runsFromAreasDialog()
    d.show()