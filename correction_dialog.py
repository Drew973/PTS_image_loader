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
        self.canvas = iface.mapCanvas()#canvas crs seems independent of project crs
        self.canvas.setDestinationCrs(crs)
        
        self.startMarker = QgsVertexMarker(self.canvas)
        self.startMarker.setIconSize(20)
        self.startMarker.setPenWidth(5)
        self.startMarker.setColor(QColor('red'))
        self.startMarker.setIconType(QgsVertexMarker.ICON_X)

        self.endMarker = QgsVertexMarker(self.canvas)
        self.endMarker.setIconSize(20)
        self.endMarker.setPenWidth(5)
        self.endMarker.setColor(QColor('green'))
        self.endMarker.setIconType(QgsVertexMarker.ICON_X)


        self.startTool = QgsMapToolEmitPoint(self.canvas)
        self.startTool.canvasClicked.connect(self.startToolClicked)
        
        self.endTool = QgsMapToolEmitPoint(self.canvas)
        self.endTool.canvasClicked.connect(self.endToolClicked)
        
        self.chainageButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.startTool))
        self.endFromMapButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.endTool))

        self.x.valueChanged.connect(self.updateEndMarker)
        self.y.valueChanged.connect(self.updateEndMarker)

        self.chainage.valueChanged.connect(self.updateStartMarker)


    def startToolClicked(self,point):
        transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
        pt = transform.transform(point)            
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
        self.x.setValue(pt.x())
        self.y.setValue(pt.y())

        
       #QModelIndex
    def setIndex(self,index):
        self.index = index
        if index.isValid() and self.model() is not None:
            m = self.model()
            r = index.row()
            self.chainage.setValue(m.index(r,m.fieldIndex('chainage')).data())
            self.x.setValue(m.index(r,m.fieldIndex('x')).data())
            self.y.setValue(m.index(r,m.fieldIndex('y')).data())
        else:
            self.chainage.setValue(0)
            self.x.setValue(0)
            self.y.setValue(0)
        
        
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
                                        x = self.x.value(),
                                        y = self.y.value()
                                        )
            
            
            
        self.hideMarkers()
        return super().accept()
        #set model values...
        
    def reject(self):
        self.hideMarkers()
        return super().reject()
        
        
        
    def updateStartMarker(self):
        self.showMarkers()
        if self.model() is not None:
            pt = self.model().getPoint(chainage = self.chainage.value(),index = self.index)
            print(pt)
            self.startMarker.setCenter(pt)
            self.canvas.refresh()
            
            
    def updateEndMarker(self):
        self.showMarkers()
        transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
        pt = transform.transform(QgsPointXY(self.x.value(),self.y.value()))
        self.endMarker.setCenter(pt)
        self.endMarker.show()
        self.canvas.refresh()
            
        
    def hide(self):
        print('hide')
        self.hideMarkers()
        return super().hide()
        #hide on map.
        #unset map tool
        
        
    def hideMarkers(self):
        self.startMarker.hide()
        self.endMarker.hide()
        self.canvas.refresh()
        
        
    def showMarkers(self):
     #   print('showMarkers')
        self.startMarker.show()
        self.endMarker.show()
        self.canvas.refresh()
        
        
    def removeMarkers(self):
        print('removeMarkers')
        self.canvas.scene().removeItem(self.startMarker)
        #iface.mapCanvas().scene().removeItem(self.endMarker)
        self.canvas.scene().removeItem(self.endMarker)
        self.canvas.refresh()
        
        #not called by accept or reject or close button...
    #def close(self):
 # #      print('close')
   #     self.removeMarkers()
       # return super().close()
        
    #QCloseEvent. called by close button.
    def closeEvent(self,event):
        self.hideMarkers()
        return super().closeEvent(event)
        
  #  def reject():
   #     super().reject()
        
    