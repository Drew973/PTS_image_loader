# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 12:00:19 2024

@author: Drew.Bennett

dialog for finding chainage+offset difference between current position and new position

QDataWidgetMapper only sets start chainage.
because model calls select() and changes row count?

"""


from PyQt5.QtWidgets import QDialog,QDoubleSpinBox,QDialogButtonBox,QFormLayout,QHBoxLayout,QPushButton,QLabel,QSpinBox,QDataWidgetMapper
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from qgis.core import QgsCoordinateReferenceSystem,QgsPointXY,QgsWkbTypes,QgsProject,QgsCoordinateTransform
from qgis.utils import iface
from image_loader import dims
from image_loader.combobox_dialog import comboBoxDialog
from image_loader.type_conversions import asFloat,asInt
from qgis.gui import QgsRubberBand , QgsMapToolEmitPoint
from image_loader import settings
from image_loader.backend import corrections_functions, gps_functions , runs_functions



def getCanvasCrs() -> QgsCoordinateReferenceSystem:
    return iface.mapCanvas().mapSettings().destinationCrs()



def horizontalLayout(widgets):
    layout = QHBoxLayout()
    for w in widgets:
        layout.addWidget(w)
    return layout



class correctionDialog(QDialog):
    
    
    def __init__(self,parent=None):
        super().__init__(parent=parent)
        self.row= None
        
    #    self.lastButton = 0
        self.gpsModel = None
        self.model = None
        self.optionsDialog = comboBoxDialog(parent = self)
        self.mapTool = None

       # self.mapTool.canvasClicked.connect(self.mapClicked)
        
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

        self.frame =  QSpinBox(self)
        self.frame.setMaximum(dims.MAX)
                
        self.line =  QSpinBox(self)
        self.line.setMaximum(dims.LINES)

        self.pixel =  QSpinBox(self)
        self.pixel.setMaximum(dims.PIXELS)

        self.startButton = QPushButton('From map...')
        self.startButton.clicked.connect(self.startButtonClicked)

        self.layout().addRow('Frame,Line,Pixel',horizontalLayout([self.frame,self.line,self.pixel,self.startButton]))

        self.endM =  QDoubleSpinBox(self)
        self.endM.setRange(-dims.MAX,dims.MAX)
        
        self.endOffset =  QDoubleSpinBox(self)
        self.endButton = QPushButton('From map...')
        self.endOffset.setRange(-99,99)

        self.endButton.clicked.connect(self.endButtonClicked)
        self.layout().addRow('New chainage,offset',horizontalLayout([self.endM,self.endOffset,self.endButton]))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addRow(buttons)
                
        self.frame.valueChanged.connect(self.redrawLine)
        self.line.valueChanged.connect(self.redrawLine)
        self.pixel.valueChanged.connect(self.redrawLine)
        self.endM.valueChanged.connect(self.redrawLine)
        self.endOffset.valueChanged.connect(self.redrawLine)
        self.redrawLine()



    def redrawLine(self):
        
        geom = corrections_functions.getCorrectionGeom(frame = self.frame.value(),
                                             line = self.line.value(),
                                             pixel = self.pixel.value(),
                                             chainage = self.endM.value(),
                                             offset = self.endOffset.value())
   
        self.markerLine.setToGeometry(geom,crs = QgsCoordinateReferenceSystem(settings.destSrid()))



    def startButtonClicked(self):
        self.mapTool = QgsMapToolEmitPoint(iface.mapCanvas())
        #tool not set if not attribute. Garbage collection?
        iface.mapCanvas().setMapTool(self.mapTool)
        self.mapTool.canvasClicked.connect(self.startFromPoint)
    
    
    def startFromPoint(self , pt : QgsPointXY):
        frame , pixel , line = corrections_functions.XYToFramePixelLine(x = pt.x() ,
                                                                        y = pt.y(),
                                                                        runPk = self.model.runPk)
        self.frame.setValue(frame)
        self.line.setValue(line)
        self.pixel.setValue(pixel)
        
        
    def endButtonClicked(self):
        self.mapTool = QgsMapToolEmitPoint(iface.mapCanvas())
        iface.mapCanvas().setMapTool(self.mapTool)
        self.mapTool.canvasClicked.connect(self.endFromPoint)
                
    
    def endFromPoint(self , pt : QgsPointXY):
        
        r = runs_functions.mRange(self.model.runPk)
        outsideRunDistance = asFloat(settings.value('outsideRunDistance') , 50.0)
        
        m , offset = gps_functions.mo( x = pt.x() ,
                                          y = pt.y() ,
            minM = r[0] - outsideRunDistance ,
            maxM = r[1] + outsideRunDistance)
            
        self.endM.setValue(m)
        self.endOffset.setValue(offset)    
        
        
    #row:int
    def setRow(self , model , row : int = -1):
        self.model = model
        self.row = row
        if row == -1:
            self.setWindowTitle('Add new correction')
        else:
            self.setWindowTitle('Edit correction')
        m = self.model
        self.frame.setValue(asInt(m.index(row,m.fieldIndex('frame')).data(),0))        
        self.line.setValue(asInt(m.index(row,m.fieldIndex('line')).data(),0))
        self.pixel.setValue(asInt(m.index(row,m.fieldIndex('pixel')).data(),0))        
        self.endM.setValue(asFloat(m.index(row,m.fieldIndex('new_chainage')).data(),0.0))        
        self.endOffset.setValue(asFloat(m.index(row,m.fieldIndex('new_offset')).data(),0.0))        



    def accept(self):
        self.hideMarker()
        self.model.setCorrection(row = self.row ,
                                 frame = self.frame.value(),
                                 line = self.line.value(),
                                 pixel = self.pixel.value(),
                                 m = self.endM.value(),
                                 offset = self.endOffset.value())
        return super().accept()

    

    def hideMarker(self):
        self.markerLine.hide()
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
        return super().reject()
    
    
    
if __name__ in ('__main__','__console__'):
    d = correctionDialog()
    d.show()