# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 13:38:09 2023

@author: Drew.Bennett


dialog to specify start/end chainage & offset

problem with LRS.
where chainage&offset is vertex of gps 1 chainage&offset : many (x,y)



"""

import os
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QColor
from qgis.gui import QgsVertexMarker,QgsMapToolEmitPoint
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject
from qgis.PyQt import uic
from PyQt5.QtCore import QModelIndex
from qgis.utils import iface
from qgis.core import Qgis

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'correction_dialog.ui'))



crs = QgsCoordinateReferenceSystem("EPSG:27700")

class correctionDialog(QDialog,FORM_CLASS):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setModel(None)

        self.setIndex(QModelIndex())
        
        self.startMarker = QgsVertexMarker(iface.mapCanvas())
        self.startMarker.setIconSize(20)
        self.startMarker.setPenWidth(5)
        self.startMarker.setColor(QColor('pink'))
        
        self.endMarker = QgsVertexMarker(iface.mapCanvas())
        self.endMarker.setIconSize(20)
        self.endMarker.setPenWidth(5)
        self.endMarker.setColor(QColor('green'))
        
        self.canvas = iface.mapCanvas()#canvas crs seems independent of project crs
        self.canvas.setDestinationCrs(crs)
        
        self.startTool = QgsMapToolEmitPoint(self.canvas)
        self.startTool.canvasClicked.connect(self.startToolClicked)
        
        self.endTool = QgsMapToolEmitPoint(self.canvas)
        self.endTool.canvasClicked.connect(self.endToolClicked)
        
        self.startFromMapButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.startTool))
        self.endFromMapButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.endTool))

        self.startChainage.valueChanged.connect(self.updateStartMarker)
        self.startOffset.valueChanged.connect(self.updateStartMarker)

        self.endChainage.valueChanged.connect(self.updateEndMarker)
        self.endOffset.valueChanged.connect(self.updateEndMarker)


    def startToolClicked(self,point):       
        if self.model() is not None:
            transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
            pt = transform.transform(point)
            co = self.model().getChainage(point=pt,index=self.index)
            print('co',co)
            if co is not None:
                chainage,offset = co
                self.startChainage.setValue(chainage)
                self.startOffset.setValue(offset)
                self.startMarker.setCenter(pt)
        else:
            print('startToolClicked. no model set...')
       
        
    def model(self):
        return self._model
        
    
    def setModel(self,model):
        self._model = model
    
    
    def endToolClicked(self,point):
        if self.model() is not None:
            transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
            pt = transform.transform(point)
            co = self.model().getChainage(point=pt,index=self.index)
            if co is not None:
                chainage,offset = co
                self.endChainage.setValue(chainage)
                self.endOffset.setValue(offset)
                self.endMarker.setCenter(pt)
        else:
            print('endToolClicked. no model set...')
        
        
       #QModelIndex
    def setIndex(self,index):
        self.index = index
        if index.isValid() and self.model() is not None:
            m = self.model()
            r = index.row()
            self.startChainage.setValue(m.index(r,m.fieldIndex('original_chainage')).data())
            self.endChainage.setValue(m.index(r,m.fieldIndex('new_chainage')).data())
            self.startOffset.setValue(m.index(r,m.fieldIndex('original_offset')).data())
            self.endOffset.setValue(m.index(r,m.fieldIndex('new_offset')).data())
        else:
            self.startChainage.setValue(0)
            self.endChainage.setValue(0)
            self.startOffset.setValue(0)
            self.endOffset.setValue(0)
        
        
    def show(self):
        self.startMarker.show()
        self.endMarker.show()
        if self.model():
            if not self.model().hasGps():
                iface.messageBar().pushMessage("Image_loader", "No GPS data. Can't display map markers.", level=Qgis.Info)
        return super().show()
        #show on map. set maptool to tool.
        
        
    def accept(self):
        if self.model():
            self.model().editCorrection(index = self.index,
                                        originalChainage = self.startChainage.value(),
                                        newChainage = self.endChainage.value(),
                                        originalOffset = self.startOffset.value(),
                                        newOffset = self.endOffset.value())
        return super().accept()
        #set model values...
        
        
    def updateStartMarker(self):
        if self.model() is not None:
            p = self.model().getPoint(chainage = self.startChainage.value(),offset=self.startOffset.value(),index=self.index)
            self.startMarker.setCenter(p)
            
            
    def updateEndMarker(self):
        if self.model() is not None:
            p = self.model().getPoint(chainage = self.endChainage.value(),offset=self.endOffset.value(),index=self.index)
            #print('p',p)
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
        
    