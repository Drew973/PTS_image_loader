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
from PyQt5.QtCore import QModelIndex,Qt
from qgis.utils import iface
from qgis.core import Qgis,QgsPointXY


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'correction_dialog.ui'))



crs = QgsCoordinateReferenceSystem("EPSG:27700")

class correctionDialog(QDialog,FORM_CLASS):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
     #   self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.setModel(None)

        self.setIndex(QModelIndex())
       # canvas = iface.mapCanvas()

        self.startMarker = QgsVertexMarker(iface.mapCanvas())
        self.startMarker.setIconSize(20)
        self.startMarker.setPenWidth(5)
        self.startMarker.setColor(QColor('red'))
        self.startMarker.setIconType(QgsVertexMarker.ICON_X)

        
        self.endMarker = QgsVertexMarker(iface.mapCanvas())
        self.endMarker.setIconSize(20)
        self.endMarker.setPenWidth(5)
        self.endMarker.setColor(QColor('green'))
        self.endMarker.setIconType(QgsVertexMarker.ICON_X)

        self.canvas = iface.mapCanvas()#canvas crs seems independent of project crs
        self.canvas.setDestinationCrs(crs)
        
        self.startTool = QgsMapToolEmitPoint(self.canvas)
        self.startTool.canvasClicked.connect(self.startToolClicked)
        
        self.endTool = QgsMapToolEmitPoint(self.canvas)
        self.endTool.canvasClicked.connect(self.endToolClicked)
        
        self.startFromMapButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.startTool))
        self.endFromMapButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.endTool))

        self.startX.valueChanged.connect(self.updateStartMarker)
        self.startY.valueChanged.connect(self.updateStartMarker)

        self.endX.valueChanged.connect(self.updateEndMarker)
        self.endY.valueChanged.connect(self.updateEndMarker)


    def startToolClicked(self,point):
        
        transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
        pt = transform.transform(point)
        
        self.startX.setValue(pt.x())
        self.startY.setValue(pt.y())
            
        if self.model() is not None:
            self.chainage.setValue(self.model().getChainage(point=pt,index=self.index))
        else:
            print('startToolClicked. no model set...')
       
        
    def model(self):
        return self._model
        
    
    def setModel(self,model):
        self._model = model
    
    
    def endToolClicked(self,point):
        transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
        pt = transform.transform(point)
        self.endX.setValue(pt.x())
        self.endY.setValue(pt.y())

        
       #QModelIndex
    def setIndex(self,index):
        self.index = index
        if index.isValid() and self.model() is not None:
            m = self.model()
            r = index.row()
            self.chainage.setValue(m.index(r,m.fieldIndex('chainage')).data())
            self.startX.setValue(m.index(r,m.fieldIndex('original_x')).data())
            self.startY.setValue(m.index(r,m.fieldIndex('original_y')).data())
            self.endX.setValue(m.index(r,m.fieldIndex('new_x')).data())
            self.endY.setValue(m.index(r,m.fieldIndex('new_y')).data())
        else:
            self.chainage.setValue(0)
            self.startX.setValue(0)
            self.startY.setValue(0)
            self.endX.setValue(0)
            self.endY.setValue(0)
        
        
    def show(self):
        self.showMarkers()
        if self.model():
            if not self.model().hasGps():
                iface.messageBar().pushMessage("Image_loader", "Load GPS data to find chainages from map clicks.", level=Qgis.Info)
        return super().show()
        #show on map. set maptool to tool.
        
        
    def accept(self):
        if self.model():
            self.model().editCorrection(index = self.index,
                                        chainage = self.chainage.value(),
                                        startX = self.startX.value(),
                                        startY = self.startY.value(),
                                        endX = self.endX.value(),
                                        endY = self.endY.value())
        return super().accept()
        #set model values...
        
        
    def updateStartMarker(self):
        self.showMarkers()
        transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
        pt = transform.transform(QgsPointXY(self.startX.value(),self.startY.value()))
        self.startMarker.setCenter(pt)

            
    def updateEndMarker(self):
        self.showMarkers()
        transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
        pt = transform.transform(QgsPointXY(self.endX.value(),self.endY.value()))
        self.endMarker.setCenter(pt)
        self.endMarker.show()

            
    def hide(self):
        self.startMarker.hide()
        self.endMarker.hide()
        return super().hide()
        #hide on map.
        #unset map tool
        
        
    def showMarkers(self):
        print('showMarkers')
        self.startMarker.show()
        self.endMarker.show()
        
    #QCloseEvent
    def closeEvent(self,event):
        iface.mapCanvas().scene().removeItem(self.startMarker)
        iface.mapCanvas().scene().removeItem(self.endMarker)
        return super().closeEvent(event)
        
  #  def reject():
   #     super().reject()
        
    