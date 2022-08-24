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
        print('setFromFeatures')
        if self.index() is not None:
            self.index().model().setFromFeatures(self.index())
            i = self.index().model().idFromFeatures(self.index())
            print(i)
            if isinstance(i,int):
                self.setValue(i)
            
            

    def contextMenuEvent(self, event):
        menu = self.lineEdit().createStandardContextMenu()
        act = menu.addAction('From selected features')
        act.triggered.connect(self.setFromFeatures)
        menu.exec_(event.globalPos())