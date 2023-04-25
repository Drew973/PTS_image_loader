# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 09:45:38 2023

@author: Drew.Bennett
"""



from qgis.gui import QgsVertexMarker,QgsMapToolEmitPoint
from qgis.core import QgsCoordinateReferenceSystem,QgsPointXY,QgsProject,QgsCoordinateTransform
from qgis.utils import iface

from PyQt5.QtWidgets import QWidget,QLabel,QPushButton,QHBoxLayout

        
class pointWidget(QWidget):
    
    def __init__(self,parent=None,crs = QgsCoordinateReferenceSystem()):
        super().__init__(parent)
        self.crs = crs
        self.point = QgsPointXY()
        
        self.label = QLabel('not set')    
        self.button = QPushButton('Click map...')
        self.setLayout(QHBoxLayout())
        
        self.layout().addWidget(self.label)
        self.layout().addWidget(self.button)


        self.tool = QgsMapToolEmitPoint(iface.mapCanvas())
        self.tool.canvasClicked.connect(self.canvasClicked)

        self.button.clicked.connect(self.buttonPressed)

        self.marker = QgsVertexMarker(iface.mapCanvas())
        self.marker.setIconSize(20)
        self.marker.setPenWidth(5)


    def buttonPressed(self):        
        iface.mapCanvas().setMapTool(self.tool)   



    def canvasClicked(self,point):#QgsPointXY
      #  print(point)
        
        #point in QgsProject.instance().crs()
        transform = QgsCoordinateTransform(QgsProject.instance().crs(),self.crs,QgsProject.instance())
        
        pt = transform.transform(point)
        
       # print(pt)
        self.point = pt
        self.label.setText('({x:.6g},{y:.6g})'.format(x = pt.x(),y = pt.y()))
        
        self.marker.setCenter(point)
        
        
    def close(self):
     #   print('close')
        
        self.marker.hide()
       # iface.mapCanvas().scene().removeItem(self.marker)
        return super().close()
    #

def test():
    
    crs = QgsCoordinateReferenceSystem('EPSG:27700')
    w = pointWidget(crs=crs)
    w.show()
    return w

if __name__ == '__console__':
    w = test()