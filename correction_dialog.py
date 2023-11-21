# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 13:38:09 2023

@author: Drew.Bennett
dialog to specify start/end chainage & offset
"""

import os
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QColor
from qgis.gui import QgsMapToolEmitPoint,QgsRubberBand
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject,QgsGeometry
from qgis.PyQt import uic
from PyQt5.QtCore import QModelIndex
from qgis.utils import iface
from qgis.core import Qgis

from image_loader.dims import lineToM,pixelToOffset
from image_loader import combobox_dialog


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
        self.pk = None
        self.run = None
        self.lastButton = None
        
        self.setModel(None)
        self.gpsModel = None
        
        self.setIndex(QModelIndex())
       # canvas = iface.mapCanvas()
        self.canvas = iface.mapCanvas()#canvas crs seems independent of project crs
        
        self.markerLine = QgsRubberBand(self.canvas,False)
        self.markerLine.setWidth(5)
        self.markerLine.setColor(QColor('red'))
        #QColor('green')

        self.canvas.setDestinationCrs(crs)

        self.mapTool = QgsMapToolEmitPoint(self.canvas)
        self.mapTool.canvasClicked.connect(self.toolClicked)
        
        self.pixelLineButton.clicked.connect(self.pixelLineButtonClicked)
        self.endButton.clicked.connect(self.endButtonClicked)
        self.frameButton.clicked.connect(self.frameButtonClicked)

        self.frameId.valueChanged.connect(self.updateMarkerLine)
        self.pixel.valueChanged.connect(self.updateMarkerLine)
        self.line.valueChanged.connect(self.updateMarkerLine)
        self.m.valueChanged.connect(self.updateMarkerLine)
        self.offset.valueChanged.connect(self.updateMarkerLine)

        
    def updateMarkerLine(self):
        if self.gpsModel is not None:
            startPt = self.gpsModel.pointFromPixelLine(pixel=self.pixel.value(),line = self.line.value(),frame=self.frameId.value())
        #    print(startM,startOffset)           
          #  print(startPt)
            endM = self.m.value()
            startM = lineToM(frame = self.frameId.value(),line = self.line.value())
            line = self.gpsModel.originalLine(startM,endM)#QgsGeometry
            if not line.isNull():
                endPt = self.gpsModel.originalPoint(m = self.m.value(),offset = self.offset.value())
                g = QgsGeometry.fromPolylineXY([startPt] + line.asPolyline() + [endPt])
                self.markerLine.setToGeometry(g,crs = crs)
                return
            #iface.messageBar().pushMessage("Image_loader", "Line too long to display.", level=Qgis.Info)
        self.markerLine.setToGeometry(QgsGeometry(),crs = crs)


    def frameButtonClicked(self):
        self.lastButton = 'frame'
        iface.mapCanvas().setMapTool(self.mapTool)

        
    def pixelLineButtonClicked(self):
        self.lastButton = 'pixelLine'
        iface.mapCanvas().setMapTool(self.mapTool)


    def endButtonClicked(self):
        self.lastButton = 'end'
        iface.mapCanvas().setMapTool(self.mapTool)


    def toolClicked(self,point):
        pt = fromCanvasCrs(point)
        if self.gpsModel is not None:
            if self.gpsModel.hasGps():
            
                if self.lastButton == 'frame':
                    frame = self.gpsModel.getFrame(pt)
                    if frame is not None:
                        self.frameId.setValue(frame)
                        self.setPixelLine(pt)
                
                if self.lastButton == 'pixelLine':
                    self.setPixelLine(pt)
    
                if self.lastButton == 'end':
                    options = self.gpsModel.locatePointOriginal(point = pt)#[(m,offset),()]
                    print('options',options)
                    m = 0
                    offset = 0
                    if len(options) == 1:
                        m = options[0][0]
                        offset = options[0][1]
                        
                    if len(options)>1:
                        r = combobox_dialog.chooseItem(items = options,title = 'Select (chainage,offset)')
                        if r is not None:
                            m = r[0]
                            offset = r[1]
                    self.m.setValue(m)
                    self.offset.setValue(offset)
            else:
                iface.messageBar().pushMessage("Image_loader", "No GPS data.", level=Qgis.Info)
                
        else:
            iface.messageBar().pushMessage("Image_loader", "GPS model not set.", level=Qgis.Info)
            iface.mapCanvas().unsetMapTool(self.mapTool)



    def setPixelLine(self,pt):
        vals = self.gpsModel.pixelLine(point=pt,frameId = self.frameId.value())
        if vals:
            self.pixel.setValue(vals[0])
            self.line.setValue(vals[1])
        
        
    def model(self):
        return self._model
        
    
    def setModel(self,model):
        self._model = model  
    
        
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
            setValue(self.frameId,m.index(r,m.fieldIndex('frame_id')))
            setValue(self.x,m.index(r,m.fieldIndex('new_x')))
            setValue(self.y,m.index(r,m.fieldIndex('new_y')))
            setValue(self.pixel,m.index(r,m.fieldIndex('pixel')))
            setValue(self.line,m.index(r,m.fieldIndex('line')))

        else:
            self.pk = None
            self.frameId.setValue(0)
            self.m.setValue(0)
            self.offset.setValue(0)
            self.pixel.setValue(0)
            self.line.setValue(0)

        
    def show(self):
        self.showMarkers()
        self.prevTool = iface.mapCanvas().mapTool()
        if self.model():
            self.updateMarkerLine()
            if not self.model().hasGps():
                iface.messageBar().pushMessage("Image_loader", "Load GPS data to find chainages from map clicks.", level=Qgis.Info)
        return super().show()
        #show on map. set maptool to tool.
        
        
    def accept(self):
        if self.model():
            self.model().setCorrection(
                                        pk = self.pk,
                                        run = self.run,
                                        frameId = self.frameId.value(),
                                        pixel = self.pixel.value(),
                                        line = self.line.value(),
                                        newM = self.m.value(),
                                        newOffset = self.offset.value()
                                        )
        return super().accept()
        #set model values...
        
        
    def done(self,r):
       self.hideMarkers()
       return super().done(r)
        
   
    def close(self):
        self.hideMarkers()
        return super().close()
   
    
    def hideMarkers(self):
        self.markerLine.hide()
        self.canvas.refresh()
        if self.prevTool is not None:
           iface.mapCanvas().setMapTool(self.prevTool,clean=True)
        
        
    def showMarkers(self):
        self.canvas.refresh()
        