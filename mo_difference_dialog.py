# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 12:00:19 2024

@author: Drew.Bennett

dialog for finding chainage+offset difference between current position and new position

QDataWidgetMapper only sets start chainage.
because model calls select() and changes row count?

"""


from PyQt5.QtWidgets import QDialog,QDoubleSpinBox,QDialogButtonBox,QFormLayout,QHBoxLayout,QPushButton,QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.core import QgsCoordinateReferenceSystem,QgsPointXY,QgsWkbTypes,QgsProject,QgsCoordinateTransform
from qgis.utils import iface
from image_loader.dims import MAX,mToFrame
from image_loader.combobox_dialog import comboBoxDialog
from image_loader.type_conversions import asFloat
from qgis.gui import QgsRubberBand , QgsMapToolEmitPoint



def getCanvasCrs() -> QgsCoordinateReferenceSystem:
    return iface.mapCanvas().mapSettings().destinationCrs()



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
        self.mapTool = QgsMapToolEmitPoint(iface.mapCanvas())

        self.mapTool.canvasClicked.connect(self.mapClicked)
        
        #new QGIS versions
        try:
            self.markerLine = QgsRubberBand(iface.mapCanvas(),QgsWkbTypes.GeometryType.Line)
        #old QGIS versions
        except Exception:
            self.markerLine = QgsRubberBand(iface.mapCanvas(),False)
        
        self.markerLine.setWidth(5)
        self.markerLine.setColor(QColor('red'))
        
        self.setLayout(QFormLayout())
        self.setWindowTitle('Find chainage and offset difference')

        self.startM =  QDoubleSpinBox(self)
        self.startM.setMaximum(MAX)
        self.startOffset =  QDoubleSpinBox(self)
        self.startButton = QPushButton('From map...')
        self.startButton.clicked.connect(self.startButtonClicked)
        self.startM.valueChanged.connect(self.recalcDifference)
        self.startM.valueChanged.connect(lambda m: self.startM.setToolTip('Frame'+str(mToFrame(m))))

        
        self.startOffset.setRange(-99,99)
        self.startOffset.valueChanged.connect(self.recalcDifference)

        self.layout().addRow('Current chainage,offset',horizontalLayout([self.startM,self.startOffset,self.startButton]))
        
        self.endM =  QDoubleSpinBox(self)
        self.endM.setRange(-MAX,MAX)
        self.endM.valueChanged.connect(self.recalcDifference)
        self.endM.valueChanged.connect(lambda m: self.endM.setToolTip('Frame'+str(mToFrame(m))))

        
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
        #2 decimal places = nearest 1cm
        self.result.setText('{m:.2f},{off:.2f}'.format(m = self.endM.value()-self.startM.value(),
                                               off = self.endOffset.value()-self.startOffset.value()))
        if hasattr(self.gpsModel,'line'):
            
            line = self.gpsModel.line(startM = self.startM.value(),
                                      startOffset = self.startOffset.value(),
                                      endM = self.endM.value(),
                                      endOffset = self.endOffset.value())
            self.markerLine.setToGeometry(line,crs = self.gpsModel.crs)


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
        
        
    def mapClicked(self , pt : QgsPointXY):
        #project to gps model crs
        t = QgsCoordinateTransform(getCanvasCrs() , self.gpsModel.crs , QgsProject.instance())
        p = t.transform(pt)  
        try:
           opts = self.model.locate(row = self.row , x = p.x(), y = p.y())
        except Exception as e:
            message = 'Image loader:Error finding (chainage,offset):'+str(e)
            iface.messageBar().pushMessage(message , duration = 5)
            return
        #print('opts',opts)
        if len(opts) == 1:
            m = opts[0,0]
            off = opts[0,1]
        if len(opts) > 1:
            m,off = self.chooseOpt(opts)
        if self.lastButton == 0:
                self.startM.setValue(m)
                self.startOffset.setValue(off)
        if self.lastButton == 1:
                self.endM.setValue(m)
                self.endOffset.setValue(off)            


    def setModel(self,model):
        self.model = model
     
           
    def setGpsModel(self,model):
        self.gpsModel = model
           
        
    #row:int
    def setRow(self,row:int = -1):
        self.row = row
        if row == -1:
            self.setWindowTitle('No run!')
        else:
            self.setWindowTitle('Edit correction for run {r}'.format(r = row+1))
        model = self.model
        self.startM.setValue(asFloat(model.index(row,model.fieldIndex('correction_start_m')).data(),0.0))        
        self.endM.setValue(asFloat(model.index(row,model.fieldIndex('correction_end_m')).data(),0.0))
        self.startOffset.setValue(asFloat(model.index(row,model.fieldIndex('correction_start_offset')).data(),0.0))
        self.endOffset.setValue(asFloat(model.index(row,model.fieldIndex('correction_end_offset')).data(),0.0))
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