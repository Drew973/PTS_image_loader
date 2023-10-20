# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 14:32:58 2023

@author: Drew.Bennett




#dialog for inserting/updating start and end chainages
#set row to None to insert,integer with runModel row to update

"""
from PyQt5.QtWidgets import QDialog,QFormLayout,QDialogButtonBox,QDoubleSpinBox,QHBoxLayout,QPushButton
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject,QgsGeometry
from qgis.utils import iface
from qgis.gui import QgsMapToolEmitPoint,QgsRubberBand
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

crs = QgsCoordinateReferenceSystem("EPSG:27700")

def fromCanvasCrs(point):
   # print('point',point)
    transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
    return transform.transform(point)



class chainagesDialog(QDialog):
    
    def __init__(self,runsModel=None,gpsModel=None,parent=None):
        super().__init__(parent=parent)
      #  self.setWindowModality(Qt.WindowModal)

        self.runsModel = runsModel
        self.setGpsModel(gpsModel)
        self.row = None
        self.lastButton = None 
        
        self.setLayout(QFormLayout())
        
        self.startChainage = QDoubleSpinBox()
        self.startButton = QPushButton('From click...')
        self.startButton.clicked.connect(self.startButtonClicked)

        startLayout = QHBoxLayout()
        startLayout.addWidget(self.startChainage)
        startLayout.addWidget(self.startButton)
        self.layout().addRow('start_chainage',startLayout)
        
        self.endChainage = QDoubleSpinBox()
        self.endButton = QPushButton('From click...')
        self.endButton.clicked.connect(self.endButtonClicked)
        endLayout = QHBoxLayout()
        endLayout.addWidget(self.endChainage)
        endLayout.addWidget(self.endButton)
        self.layout().addRow('end_chainage',endLayout)
        
        
        self.canvas = iface.mapCanvas()#canvas crs seems independent of project crs
        self.markerLine = QgsRubberBand(self.canvas,False)
        self.markerLine.setWidth(5)
        self.markerLine.setColor(QColor('red'))
        self.canvas.setDestinationCrs(crs)

        self.mapTool = QgsMapToolEmitPoint(self.canvas)
        self.mapTool.canvasClicked.connect(self.toolClicked)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.layout().addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.startChainage.valueChanged.connect(self.updateLine)
        self.endChainage.valueChanged.connect(self.updateLine)

        
        
    def setGpsModel(self,model):
        self.gpsModel = model
        self.updateLimits()


    def toolClicked(self,point):
        if self.gpsModel is not None:
            pt = fromCanvasCrs(point)
            if self.lastButton == 'start':
                self.startChainage.setValue(self.gpsModel.getOriginalChainage(pt)[0])   
            if self.lastButton == 'end':
                self.endChainage.setValue(self.gpsModel.getOriginalChainage(pt)[0])
                
                
    def endButtonClicked(self):
        self.lastButton = 'end'
        iface.mapCanvas().setMapTool(self.mapTool)
        
        
    def startButtonClicked(self):
        self.lastButton = 'start'
        iface.mapCanvas().setMapTool(self.mapTool)

        
    def updateLimits(self):
        if self.gpsModel is not None:
            limits = self.gpsModel.chainageLimits()
            self.startChainage.setRange(limits[0],limits[1])
            self.endChainage.setRange(limits[0],limits[1])
            
            
    def setRow(self,row):
        self.row = row
        if row is None:
            self.setWindowTitle('Add run')
        else:
            self.setWindowTitle('Edit chainages for run {run}'.format(run=row+1))
            self.startChainage.setValue(self.runsModel.index(row,self.runsModel.fieldIndex('start_chainage')).data())
            self.endChainage.setValue(self.runsModel.index(row,self.runsModel.fieldIndex('end_chainage')).data())
            
            
    def show(self):
        self.updateLimits()
        self.markerLine.show()
        return super().show()
            
            
    def accept(self):
        if self.runsModel is not None:
            if self.row is None:
                self.runsModel.addRuns([{'start_chainage':self.startChainage.value(),'end_chainage':self.endChainage.value()}])
            else:
                self.runsModel.setData(self.runsModel.index(self.row,self.runsModel.fieldIndex('start_chainage')),self.startChainage.value())                
                self.runsModel.setData(self.runsModel.index(self.row,self.runsModel.fieldIndex('end_chainage')),self.endChainage.value())
        return super().accept()


    def updateLine(self):
        if self.gpsModel is not None:
            line = self.gpsModel.originalLine(self.startChainage.value(),self.endChainage.value())
            self.markerLine.setToGeometry(line,crs = crs)
    
    
    def done(self,r):
        self.markerLine.hide()
        self.canvas.refresh()
        return super().done(r)