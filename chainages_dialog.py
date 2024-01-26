# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 14:32:58 2023

@author: Drew.Bennett




#dialog for inserting/updating start and end chainages
#set row to None to insert,integer with runModel row to update

"""
from PyQt5.QtWidgets import QDialog,QFormLayout,QDialogButtonBox,QSpinBox,QHBoxLayout,QPushButton
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject,QgsGeometry
from qgis.utils import iface
from qgis.gui import QgsMapToolEmitPoint,QgsRubberBand
from PyQt5.QtGui import QColor
from image_loader.dims import frameToM


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
        
        self.startChainage.setRange(0,999999999)
        self.endChainage.setRange(0,999999999)
        
        
    def setGpsModel(self,model):
        self.gpsModel = model



    def toolClicked(self,point):
        if self.gpsModel is not None:
            pt = fromCanvasCrs(point)
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
            self.startChainage.setValue(self.runsModel.index(row,self.runsModel.fieldIndex('start_frame')).data())
            self.endChainage.setValue(self.runsModel.index(row,self.runsModel.fieldIndex('end_frame')).data())
            
            
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
        s = frameToM(self.startChainage.value())
        e = frameToM(self.endChainage.value())
        if self.gpsModel is not None and s<e :
            line = self.gpsModel.line(startM = s , endM = e)
#            print('line',line)
            self.markerLine.setToGeometry(line,crs = crs)
        else:
            self.markerLine.setToGeometry(QgsGeometry())
    
    
    def done(self,r):
        self.markerLine.hide()
        self.canvas.refresh()
        return super().done(r)