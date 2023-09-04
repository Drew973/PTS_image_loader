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

def fromCanvasCrs(point):
   # print('point',point)
    transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
    return transform.transform(point)


def toCanvasCrs(point):
   # print('point',point)
    transform = QgsCoordinateTransform(crs,QgsProject.instance().crs(),QgsProject.instance())
    return transform.transform(point)



class correctionDialog(QDialog,FORM_CLASS):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)
     #   self.setAttribute(Qt.WA_DeleteOnClose)
        self.prevTool = None
        self.setModel(None)
        self.setIndex(QModelIndex())
        self.pk = None

       # canvas = iface.mapCanvas()
        self.canvas = iface.mapCanvas()#canvas crs seems independent of project crs
        self.canvas.setDestinationCrs(crs)
        
        self.startMarker = QgsVertexMarker(self.canvas)
        self.startMarker.setIconSize(20)
        self.startMarker.setPenWidth(5)
        self.startMarker.setColor(QColor('red'))
        self.startMarker.setIconType(QgsVertexMarker.ICON_CROSS)

        self.endMarker = QgsVertexMarker(self.canvas)
        self.endMarker.setIconSize(20)
        self.endMarker.setPenWidth(5)
        self.endMarker.setColor(QColor('green'))
        self.endMarker.setIconType(QgsVertexMarker.ICON_X)

        self.startTool = QgsMapToolEmitPoint(self.canvas)
        self.startTool.canvasClicked.connect(self.startToolClicked)
        
        self.endTool = QgsMapToolEmitPoint(self.canvas)
        self.endTool.canvasClicked.connect(self.endToolClicked)
        
        self.currentButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.startTool))
        self.endButton.clicked.connect(lambda:iface.mapCanvas().setMapTool(self.endTool))

        self.chainage.valueChanged.connect(self.updateStartMarker)
        self.xOffset.valueChanged.connect(self.updateStartMarker)
        self.yOffset.valueChanged.connect(self.updateStartMarker)
        self.x.valueChanged.connect(self.updateEndMarker)
        self.y.valueChanged.connect(self.updateEndMarker)
        
    def startToolClicked(self,point):   
        pt = fromCanvasCrs(point)       
        if self.model() is not None:
            ch,xo,yo = self.model().getChainage(point=pt,index=self.index)
            self.chainage.setValue(ch)
            self.xOffset.setValue(xo)
            self.yOffset.setValue(yo)
        else:
            print('chainage tool clicked but no model set...')

        
    def model(self):
        return self._model
        
    
    def setModel(self,model):
        self._model = model
    
    
    def endToolClicked(self,point):
        pt = fromCanvasCrs(point)
        self.x.setValue(pt.x())
        self.y.setValue(pt.y())

        
       #QModelIndex
    def setIndex(self,index):
        
        def setValue(spinbox,index):
            try:
                spinbox.setValue(float(index.data()))
            except Exception:
                pass
        
        self.index = index
        if index.isValid() and self.model() is not None:
            m = self.model()
            r = index.row()
            self.pk = m.index(r,m.fieldIndex('pk')).data()
            setValue(self.chainage,m.index(r,m.fieldIndex('chainage')))
            setValue(self.x,m.index(r,m.fieldIndex('new_x')))
            setValue(self.y,m.index(r,m.fieldIndex('new_y')))
            setValue(self.xOffset,m.index(r,m.fieldIndex('x_offset')))
            setValue(self.yOffset,m.index(r,m.fieldIndex('y_offset')))

        else:
            self.pk = None
            self.chainage.setValue(0)
            self.x.setValue(0)
            self.y.setValue(0)
            self.xOffset.setValue(0)
            self.yOffset.setValue(0)

        
    def show(self):
        self.showMarkers()
        self.prevTool = iface.mapCanvas().mapTool()
        
        
        if self.model():
            self.updateStartMarker()#images moved/points changed after georeferencing            
            if not self.model().hasGps():
                iface.messageBar().pushMessage("Image_loader", "Load GPS data to find chainages from map clicks.", level=Qgis.Info)
        return super().show()
        #show on map. set maptool to tool.
        
        
    def accept(self):
        if self.model():
            self.model().setCorrection(
                                        pk = self.pk,
                                        chainage = self.chainage.value(),
                                        xOffset = self.xOffset.value(),
                                        yOffset = self.yOffset.value(),
                                        newX = self.x.value(),
                                        newY = self.y.value()
                                        )
        self.hideMarkers()
        return super().accept()
        #set model values...
        
    #close button also calls this.
    def reject(self):
        self.hideMarkers()
        return super().reject()
        
        
    def updateStartMarker(self):
        if self.model() is not None:
            pt = self.model().getPoint(chainage = self.chainage.value(),
                                       xOffset = self.xOffset.value(),
                                       yOffset = self.yOffset.value(),
                                       index = self.index)
            
            self.startMarker.setCenter(toCanvasCrs(pt))
            self.showMarkers()

            
    def updateEndMarker(self):
        pt = QgsPointXY(self.x.value(),self.y.value())
        self.endMarker.setCenter(toCanvasCrs(pt))
        self.showMarkers()

        
    def hide(self):
      #  print('hide')
        self.hideMarkers()
        
        return super().hide()
        #hide on map.
        #unset map tool
        
        
    def hideMarkers(self):
        self.startMarker.hide()
        self.endMarker.hide()
        self.canvas.refresh()
        if self.prevTool is not None:
           iface.mapCanvas().setMapTool(self.prevTool,clean=True)

        
    def showMarkers(self):
     #   print('showMarkers')
        self.startMarker.show()
        self.endMarker.show()
        self.canvas.refresh()
        
        
    def removeMarkers(self):
      #  print('removeMarkers')
        self.canvas.scene().removeItem(self.startMarker)
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
        
    