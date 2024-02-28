# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 12:00:19 2024

@author: Drew.Bennett



QDataWidgetMapper only sets start chainage.
because model calls select() and changes row count?

"""


from PyQt5.QtWidgets import QDialog,QDoubleSpinBox,QDialogButtonBox,QFormLayout,QHBoxLayout,QPushButton,QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.gui import QgsMapToolEmitPoint,QgsRubberBand
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject
from qgis.utils import iface
from image_loader.dims import MAX
from image_loader.combobox_dialog import comboBoxDialog
#import numpy as np


crs = QgsCoordinateReferenceSystem("EPSG:27700")
def fromCanvasCrs(point):
   # print('point',point)
    transform = QgsCoordinateTransform(QgsProject.instance().crs(),crs,QgsProject.instance())
    return transform.transform(point)


def toCanvasCrs(point):
   # print('point',point)
    transform = QgsCoordinateTransform(crs,QgsProject.instance().crs(),QgsProject.instance())
    return transform.transform(point)

def horizontalLayout(widgets):
    layout = QHBoxLayout()
    for w in widgets:
        layout.addWidget(w)
    return layout



class moDifferenceDialog(QDialog):
    
    
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.pk = None
        self.row= None
        
        
        self.lastButton = 0
        self.gpsModel = None
        
        self.optionsDialog = comboBoxDialog(parent = self)
        
       # self.wrapper = QDataWidgetMapper()
      #  self.wrapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        
        self.canvas = iface.mapCanvas()#canvas crs seems independent of project crs
        
        self.mapTool = QgsMapToolEmitPoint(self.canvas)
        self.mapTool.canvasClicked.connect(self.mapClicked)
        
        
        self.markerLine = QgsRubberBand(self.canvas,False)
        self.markerLine.setWidth(5)
        self.markerLine.setColor(QColor('red'))
        #QColor('green')

        self.canvas.setDestinationCrs(crs)
        
        self.setLayout(QFormLayout())
        self.setWindowTitle('Find chainage and offset difference')

        self.startM =  QDoubleSpinBox(self)
        self.startM.setMaximum(MAX)
        self.startOffset =  QDoubleSpinBox(self)
        self.startButton = QPushButton('From map...')
        self.startButton.clicked.connect(self.startButtonClicked)
        self.startM.valueChanged.connect(self.recalcDifference)
        self.startOffset.setRange(-99,99)
        self.startOffset.valueChanged.connect(self.recalcDifference)

        self.layout().addRow('Current chainage,offset',horizontalLayout([self.startM,self.startOffset,self.startButton]))
        
        self.endM =  QDoubleSpinBox(self)
        self.endM.setRange(-MAX,MAX)
        self.endM.valueChanged.connect(self.recalcDifference)
        self.endOffset =  QDoubleSpinBox(self)
        self.endButton = QPushButton('From map...')
        self.endOffset.setRange(-99,99)

        self.endButton.clicked.connect(self.endButtonClicked)
        self.endOffset.valueChanged.connect(self.recalcDifference)
        self.layout().addRow('New chainage,offset',horizontalLayout([self.endM,self.endOffset,self.endButton]))

        self.result = QLabel(self)
        self.result.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout().addRow('Difference',self.result)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addRow(buttons)
        self.recalcDifference()


    def recalcDifference(self):
        self.result.setText('{m},{off}'.format(m = self.endM.value()-self.startM.value(),
                                               off = self.endOffset.value()-self.startOffset.value()))

        if hasattr(self.gpsModel,'line'):
            
         #  startMO = self.model.unCorrectMO(np.array([[self.startM.value(),self.startOffset.value()]]))
           # print('startMO',startMO)
            
            line = self.gpsModel.line(startM = self.startM.value(),
                                      startOffset = self.startOffset.value(),
                                      endM = self.endM.value(),
                                      endOffset = self.endOffset.value())
            self.markerLine.setToGeometry(line,crs=crs)


    def startButtonClicked(self):
        self.lastButton = 0
        iface.mapCanvas().setMapTool(self.mapTool)
    
    
    def endButtonClicked(self):
        self.lastButton = 1
        iface.mapCanvas().setMapTool(self.mapTool)
        
        
        
    def chooseOpt(self,opts):
        self.optionsDialog.box.clear()
        self.optionsDialog.box.addItems([str(row) for row in opts])
        r = self.optionsDialog.exec()
        if r == QDialog.Accepted:
            i = self.optionsDialog.box.currentIndex()
            if i != -1:
                return (opts[i,0],opts[i,1])
        return (0.0,0.0)                   
        
        
    def mapClicked(self,pt):
       # print('pt',pt)
     #   print('gpsModel',self.gpsModel)
        if hasattr(self.model,'locate'):
            p = fromCanvasCrs(pt)            
            #self.model.index(self.model.fieldIndex('start_frame')).data
           # rg = self.model.chainageRange(self.row)
        #    print('rg',rg)
            
            
            if self.lastButton == 0:
                opts = self.model.locate(row=self.row,pt=p,corrected = False)
            #    opts = self.model.correctMO(opts)
                
                if len(opts) == 1:
                    self.startM.setValue(opts[0,0])
                    self.startOffset.setValue(opts[0,1])
                if len(opts) >1:
                    m,off = self.chooseOpt(opts)
                    self.startM.setValue(m)
                    self.startOffset.setValue(off)

                    
            if self.lastButton == 1:
                opts = self.model.locate(row=self.row,pt=p,corrected = False)
                if len(opts) == 1:
                    self.endM.setValue(opts[0,0])
                    self.endOffset.setValue(opts[0,1])
                if len(opts) >1:
                    m,off = self.chooseOpt(opts)
                    self.endM.setValue(m)
                    self.endOffset.setValue(off)            
            

    def setModel(self,model):
        self.model = model
     
           
    def setGpsModel(self,model):
        self.gpsModel = model
           
    #row:int
    def setRow(self,row = -1):
        self.row = row
        model = self.model
        
        #name:str->float
        def val(name,default = 0.0):
            d = model.index(row,model.fieldIndex(name)).data()
            if isinstance(d,float):
                return d
            return default
        
        self.startM.setValue(val('correction_start_m'))
        self.endM.setValue(val('correction_end_m'))
        self.startOffset.setValue(val('correction_start_offset'))
        self.endOffset.setValue(val('correction_end_offset'))
        self.pk = model.index(row,model.fieldIndex('pk')).data()


    def accept(self):
        self.hideMarker()
        if self.pk is not None:
            self.model.setCorrection(pk = self.pk,startM = self.startM.value(),endM = self.endM.value(),
                                     startOffset = self.startOffset.value(),endOffset = self.endOffset.value())
        return super().accept()
    
    
    def hideMarker(self):
        self.markerLine.hide()
        #iface.mapCanvas().scene().removeItem(self.markerLine)
        if iface.mapCanvas().mapTool() == self.mapTool:
            iface.mapCanvas().setMapTool(None,clean = True)


    def showMarker(self):
        self.markerLine.show()
        
        
    def show(self):
        self.showMarker()
        super().show()
        
        
    def hide(self):
        self.hideMarker()
        return super().hide()

        
    def reject(self):
        self.hideMarker()
        self.setRow(self.row)
        return super().reject()
    
    
if __name__ in ('__main__','__console__'):
    d = moDifferenceDialog()
    d.show()