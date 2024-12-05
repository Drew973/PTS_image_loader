# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 10:05:27 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit,QCheckBox,QDoubleSpinBox


from qgis.gui import QgsProjectionSelectionWidget
from qgis.core import QgsCoordinateReferenceSystem

from image_loader.type_conversions import asFloat , asBool , asInt

from PyQt5.QtCore import QSettings
settings = QSettings("pts" , "image_loader")


class settingsDialog(QDialog):
        
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle('Image loader settings')
        self.setLayout(QFormLayout(self))
        self.folder = QLineEdit()
        self.layout().addRow('Project folder',self.folder)
                
        self.startAtZero = QCheckBox()
        t = '''
        Tick to start images closer to where they should be.
        Untick if compatibility with versions < 3.36 and collator required.
        '''
        self.startAtZero.setToolTip(t)
        self.startAtZero.setChecked(asBool(settings.value('startAtZero') , True))
        self.layout().addRow('Shift chainages to start at 0 when loading GPS' , self.startAtZero)
        
        self.maxOffset = QDoubleSpinBox()
        self.maxOffset.setValue(asFloat(settings.value('maxOffset') , 10.0))
        self.layout().addRow('Maximum offset when finding chainage from map click. In meters.' , self.maxOffset)

        self.outsideRunDistance = QDoubleSpinBox()
        self.outsideRunDistance.setValue(asFloat(settings.value('outsideRunDistance') , 50.0))
        self.layout().addRow(r'Look this far (in meters) outside run start/end chainage when finding corrections.',self.outsideRunDistance)
        
        self.crsWidget = QgsProjectionSelectionWidget()        
        crs : QgsCoordinateReferenceSystem = QgsCoordinateReferenceSystem()
        crs.createFromSrid(asInt(settings.value('destSrid') , 27700))
        self.crsWidget.setCrs(crs)

        self.layout().addRow('Projection for georeferenced images. Needs units of meters.' , self.crsWidget)
        
       # self.crsWidget.crs().isGeographic()

        
    def crs(self) -> QgsCoordinateReferenceSystem:
        return self.crsWidget.crs()
   
     
    def srid(self) -> int:
        return self.crs().postgisSrid()
    
    
    def closeEvent(self,event):
        settings.setValue('folder',self.folder.text())
        settings.setValue('startAtZero',self.startAtZero.isChecked())
        settings.setValue('maxOffset',self.maxOffset.value())
        settings.setValue('outsideRunDistance',self.outsideRunDistance.value())
        settings.setValue('destSrid' , self.srid())# like 27700
        super().closeEvent(event)
     
    
def test():
    d = settingsDialog()
    d.show()
    return d
    
    
if __name__=='__console__':
    d = test()
    
    
    