# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 13:38:09 2023

@author: Drew.Bennett
"""

import os
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QColor
from qgis.gui import QgsVertexMarker,QgsMapToolEmitPoint
from qgis.utils import iface
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject
from qgis.PyQt import uic
from PyQt5.QtCore import QModelIndex


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'correction_dialog.ui'))



crs = QgsCoordinateReferenceSystem("EPSG:27700")

class correctionDialog(QDialog,FORM_CLASS):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setIndex(QModelIndex())
        
        
        self.startMarker = QgsVertexMarker(iface.mapCanvas())
        self.startMarker.setIconSize(20)
        self.startMarker.setPenWidth(5)
        
        
        self.endMarker = QgsVertexMarker(iface.mapCanvas())
        self.endMarker.setIconSize(20)
        self.endMarker.setPenWidth(5)
        self.endMarker.setColor(QColor('green'))
        
        self.startTool = QgsMapToolEmitPoint(iface.mapCanvas())
        self.startTool.canvasClicked.connect(self.startToolClicked)
        
        self.endTool = QgsMapToolEmitPoint(iface.mapCanvas())
        self.endTool.canvasClicked.connect(self.endToolClicked)
        
        self.startFromMapButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.startTool))
        self.endFromMapButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.endTool))


        self.startChainage.valueChanged.connect(self.updateStartMarker)
        self.startOffset.valueChanged.connect(self.updateStartMarker)

        self.endChainage.valueChanged.connect(self.updateEndMarker)
        self.endOffset.valueChanged.connect(self.updateEndMarker)



    def startToolClicked(self,point):       
        if self.index.model() is not None:
            transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
            pt = transform.transform(point)
            co = self.index.model().getChainage(point=pt,index=self.index)
            if co is not None:
                chainage,offset = co
                self.startChainage.setValue(chainage)
                self.startOffset.setValue(offset)
        else:
            print('startToolClicked. no index set...')
       
        
    def endToolClicked(self,point):
        if self.index.model() is not None:
            transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
            pt = transform.transform(point)
            co = self.index.model().getChainage(point=pt,index=self.index)
            if co is not None:
                chainage,offset = co
                self.endChainage.setValue(chainage)
                self.endOffset.setValue(offset)
        else:
            print('endToolClicked. no index set...')
        
       
    def setIndex(self,index):
        self.index = index
        
        
    def show(self):
        self.startMarker.show()
        self.endMarker.show()
        return super().show()
        #show on map. set maptool to tool.
        
        
  #  def accept(self):
     #   super().accept()
        #set model values...
        
        
        
    def updateStartMarker(self):
        if self.index.model() is not None:
            p = self.index.model().getPoint(chainage = self.startChainage.value(),offset=self.startOffset.value(),index=self.index)
            self.startMarker.setCenter(p)
            
            
    def updateEndMarker(self):
        if self.index.model() is not None:
            p = self.index.model().getPoint(chainage = self.endChainage.value(),offset=self.endOffset.value(),index=self.index)
            self.endMarker.setCenter(p)
            
            
    def hide(self):
        self.startMarker.hide()
        self.endMarker.hide()
        return super().hide()
    
        #hide on map.
        #unset map tool
        
    #QCloseEvent
    def closeEvent(self,event):
        iface.mapCanvas().scene().removeItem(self.startMarker)
        iface.mapCanvas().scene().removeItem(self.endMarker)
        return super().closeEvent(event)
        
  #  def reject():
   #     super().reject()
        
    