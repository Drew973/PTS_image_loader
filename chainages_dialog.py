# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 14:32:58 2023

@author: Drew.Bennett




#dialog for inserting/updating start and end chainages
#set row to None to insert,integer with runModel row to update

"""
from PyQt5.QtWidgets import QDialog,QFormLayout,QDialogButtonBox,QSpinBox,QHBoxLayout,QPushButton
from qgis.core import QgsCoordinateReferenceSystem,QgsGeometry,QgsWkbTypes,QgsProject,QgsCoordinateTransform
from qgis.utils import iface
from qgis.gui import QgsRubberBand , QgsMapToolEmitPoint
from PyQt5.QtGui import QColor
from image_loader import dims
from image_loader.type_conversions import asInt


def getCanvasCrs() -> QgsCoordinateReferenceSystem:
    return iface.mapCanvas().mapSettings().destinationCrs()


class chainagesDialog(QDialog):
    
    def __init__(self,runsModel=None,gpsModel=None,parent=None):
        super().__init__(parent=parent)
      #  self.setWindowModality(Qt.WindowModal)

        self.runsModel = runsModel
        self.setGpsModel(gpsModel)
        self.row = -1
        self.lastButton = None 
        
        self.setLayout(QFormLayout())
        
        self.startChainage = QSpinBox()
        self.startButton = QPushButton('From click...')
        self.startButton.clicked.connect(self.startButtonClicked)

        startLayout = QHBoxLayout()
        startLayout.addWidget(self.startChainage)
        startLayout.addWidget(self.startButton)
        self.layout().addRow('start_frame',startLayout)
        
        self.endChainage = QSpinBox()
        self.endButton = QPushButton('From click...')
        self.endButton.clicked.connect(self.endButtonClicked)
        endLayout = QHBoxLayout()
        endLayout.addWidget(self.endChainage)
        endLayout.addWidget(self.endButton)
        self.layout().addRow('end_frame',endLayout)
        
        #QgsRubberBand() changed between qgis versions. somewhere between 3.18:3 and 3.34.        
        try:
            self.markerLine = QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.GeometryType.Line)#new versions
        except Exception as te:
            self.markerLine = QgsRubberBand(iface.mapCanvas(),False)#old versions
        self.markerLine.setWidth(5)
        self.markerLine.setColor(QColor('red'))

        self.mapTool = QgsMapToolEmitPoint(iface.mapCanvas())
        self.mapTool.canvasClicked.connect(self.toolClicked)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.layout().addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.startChainage.valueChanged.connect(self.updateLine)
        self.endChainage.valueChanged.connect(self.updateLine)
        self.startChainage.setRange(0,dims.MAX)
        self.endChainage.setRange(0,dims.MAX)
        
        
    def setGpsModel(self,model):
        self.gpsModel = model


    def toolClicked(self,point):
        if self.gpsModel is not None:
            t = QgsCoordinateTransform(getCanvasCrs() , self.gpsModel.crs , QgsProject.instance())
            pt = t.transform(point)
            f = self.gpsModel.pointToFrame(pt)
            if self.lastButton == 'start':
                self.startChainage.setValue(f)
            if self.lastButton == 'end':
                self.endChainage.setValue(f)
                
                
    def endButtonClicked(self):
        self.lastButton = 'end'
        iface.mapCanvas().setMapTool(self.mapTool)
        
        
    def startButtonClicked(self):
        self.lastButton = 'start'
        iface.mapCanvas().setMapTool(self.mapTool)

            
    def setRow(self,row):
        self.row = row
        if row is None:
            self.setWindowTitle('Add run')
        else:
            self.setWindowTitle('Edit frames for run {run}'.format(run=row+1))
            self.startChainage.setValue(asInt(self.runsModel.index(row,self.runsModel.fieldIndex('start_frame')).data()))
            self.endChainage.setValue(asInt(self.runsModel.index(row,self.runsModel.fieldIndex('end_frame')).data()))
            
            
    def show(self):
        self.markerLine.show()
        return super().show()
            
            
    def accept(self):
        if self.runsModel is not None:
            if self.row is None:
                self.runsModel.addRuns([{'start_frame':self.startChainage.value(),'end_frame':self.endChainage.value()}])
            else:
                self.runsModel.setData(self.runsModel.index(self.row,self.runsModel.fieldIndex('start_frame')),self.startChainage.value())                
                self.runsModel.setData(self.runsModel.index(self.row,self.runsModel.fieldIndex('end_frame')),self.endChainage.value())
        return super().accept()


    def updateLine(self):
        s = dims.frameToM(self.startChainage.value())
        e = dims.frameToM(self.endChainage.value()+1)
        if self.gpsModel is not None and s<e :
            line = self.gpsModel.centerLine(startM = s , endM = e)
#            print('line',line)
            self.markerLine.setToGeometry(line,crs = self.gpsModel.crs)
        else:
            self.markerLine.setToGeometry(QgsGeometry())
    
    
    def done(self,r):
        self.markerLine.hide()
        iface.mapCanvas().refresh()
        return super().done(r)