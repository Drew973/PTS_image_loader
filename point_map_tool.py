# -*- coding: utf-8 -*-
"""
Created on Thu Jun 20 09:21:33 2024

@author: Drew.Bennett

A better version of QgsMapToolEmitPoint. When mouse button released on map transforms point to destCrs and emits canvasReleased.

QgsMapToolEmitPoint documentation unclear on what CRS the emited points are in.


"""
from PyQt5.QtCore import pyqtSignal
from qgis.gui import QgsMapMouseEvent , QgsMapTool , QgsMapCanvas
from qgis.core import QgsPointXY , QgsCoordinateReferenceSystem , QgsProject , QgsCoordinateTransform
from qgis.utils import iface



class pointMapTool(QgsMapTool):
    
    canvasReleased = pyqtSignal(QgsPointXY)
    
    def __init__(self, destCrs:QgsCoordinateReferenceSystem,canvas:QgsMapCanvas = None):
        if canvas is None:
            canvas = iface.mapCanvas()        
        super().__init__(canvas)
        self.crs = destCrs
        
        
    def canvasReleaseEvent(self, e: QgsMapMouseEvent):
        mapPoint: QgsPointXY = e.mapPoint()
        canvasCrs:QgsCoordinateReferenceSystem = self.canvas().mapSettings().destinationCrs()
        #print('canvasCrs',canvasCrs)
        #print('p',mapPoint)
        transform = QgsCoordinateTransform(canvasCrs,self.crs,QgsProject.instance())
        transformedPoint = transform.transform(mapPoint)
        #print('transformedPoint',transformedPoint)
        self.canvasReleased.emit(transformedPoint)

#snapToGrid(self, precision: float, crs: QgsCoordinateReferenceSystem)




if __name__ == '__console__':
    crs = QgsCoordinateReferenceSystem("EPSG:27700")
    tool = pointMapTool(destCrs = crs)
    iface.mapCanvas().setMapTool(tool)

    def printPoint(point):
        print('point clicked:',point)
       
    tool.canvasReleased.connect(printPoint)
        
        