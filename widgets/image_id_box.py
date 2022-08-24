# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 13:34:22 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QSpinBox




class imageIdBox(QSpinBox):  
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        
    def index(self):
        return self._index
        
    
    def setIndex(self,index):
        self._index = index
       
        v = index.model().minValue(index)
        if isinstance(v,int):
            self.setMinimum(v)
        
        v = index.model().maxValue(index)
        if isinstance(v,int):
            self.setMaximum(v)
            
        self.setValue(int(index.data()))


    def setFromFeatures(self):
        if self.index() is not None:
            self.index().model().setFromFeatures(self.index())
            i = self.index().model().idFromFeatures(self.index())
            if isinstance(i,int):
                self.setValue(i)
            
    
    def setToMax(self):
        self.setValue(self.maximum())
        
        
    def setToMin(self):
        self.setValue(self.minimum())
        
        
    def contextMenuEvent(self, event):
        menu = self.lineEdit().createStandardContextMenu()
        toMaxAct = menu.addAction('Set to maximum')
        toMaxAct.triggered.connect(self.setToMax)
        toMinAct = menu.addAction('Set to mimumum')
        toMinAct.triggered.connect(self.setToMin)
        fromFeaturesAct = menu.addAction('From selected features')
        fromFeaturesAct.triggered.connect(self.setFromFeatures)
        menu.exec_(event.globalPos())