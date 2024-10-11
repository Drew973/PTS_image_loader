# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 10:05:27 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit,QCheckBox,QDoubleSpinBox
from PyQt5.QtCore import QSettings

from image_loader.type_conversions import asFloat , asBool



class settingsDialog(QDialog):
        
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLayout(QFormLayout(self))
        self.settings = QSettings("pts","image_loader")
        
        self.folder = QLineEdit()
       # self.folder.setText(r'D:\RAF Shawbury')####################################remove before release
        self.layout().addRow('Project folder',self.folder)
        
        
        self.startAtZero = QCheckBox()
        t = '''
        Tick to start images closer to where they should be.
        Untick if compatibility with versions < 3.36 and collator required.
        '''
        self.startAtZero.setToolTip(t)   
        self.startAtZero.setChecked(asBool(self.settings.value('startAtZero'),True))
        self.layout().addRow('Shift chainages to start at 0 when loading GPS',self.startAtZero)
        
        self.maxOffset = QDoubleSpinBox()
        self.maxOffset.setValue(asFloat(self.settings.value('maxOffset'),10.0))
        self.layout().addRow('Maximum offset (in meters) when finding chainage from map click.',self.maxOffset)

        self.outsideRunDistance = QDoubleSpinBox()
        self.outsideRunDistance.setValue(asFloat(self.settings.value('outsideRunDistance'),50.0))
        self.layout().addRow(r'Look this far (in meters) outside run start/end when finding corrections.',self.outsideRunDistance)
        
        
    def closeEvent(self,event):
        self.settings.setValue('startAtZero',self.startAtZero.isChecked())
        self.settings.setValue('maxOffset',self.maxOffset.value())
        self.settings.setValue('outsideRunDistance',self.outsideRunDistance.value())
        super().closeEvent(event)
     
        
    #dict like.
    def __getitem__ (self,key):
       # return self.fields()[key]
        if key == 'folder':
            return self.folder.text()
        if key == 'startAtZero':
            return self.startAtZero.isChecked()
        raise KeyError('settingsDialog has no field '+str(key))    
    
def test():
    d = settingsDialog()
    d.show()
    return d
    
    
if __name__=='__console__':
    d = test()
    
    
    