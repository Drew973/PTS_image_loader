# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 08:16:19 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QModelIndex


from image_loader import details_tree_model
#import sys

#sys.path.append('..')


from PyQt5.QtWidgets import QSpinBox,QHBoxLayout,QPushButton




class imageIdBox(QSpinBox):  
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        
    def index(self):
        return self._index
        
    
    def setIndex(self,index):
        self._index = index
        self.setRange(index.model().valueRange(index))
        self.setValue(int(index.data()))


    def setToMax(self):
        self.setValue(self.maximum())
        
        
    def setToMin(self):
        self.setValue(self.minimum())
        
        
    def contextMenuEvent(self, event):
        menu = self.lineEdit().createStandardContextMenu()
        toMaxAct = menu.addAction('Set to maximum')
        toMaxAct.triggered.connect(self.setToMax)
        toMinAct = menu.addAction('Set to minimum')
        toMinAct.triggered.connect(self.setToMin)
        menu.exec_(event.globalPos())



class setBetweenDialog(QDialog):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.setLayout(QHBoxLayout(self))
        
        self.index = QModelIndex()
        
        self.startBox = imageIdBox()
        self.startBox.setToolTip('Start Id')
        self.layout().addWidget(self.startBox)
        self.startBox.valueChanged.connect(self.startSet)
        
        self.endBox = imageIdBox()
        self.endBox.setToolTip('End Id')

        self.layout().addWidget(self.endBox)
        self.endBox.valueChanged.connect(self.endSet)
        
        self.okButton = QPushButton('Ok')
        self.layout().addWidget(self.okButton)
        self.okButton.clicked.connect(self.accept)

        self.cancelButton = QPushButton('Cancel')
        self.layout().addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.reject)

        
        
        
    def setIndex(self,index):
        self.index = index
        minId,maxId = index.model().valueRange(index)
        
        self.startBox.setRange(minId,maxId)
        
        s = index.data(details_tree_model.startRole)
        if s is None:
            s = minId
        self.startBox.setValue(s)
        
        
        self.endBox.setRange(minId,maxId)
        e = index.data(details_tree_model.endRole)
        if e is None:
            e = minId
        self.endBox.setValue(e)
        

    
    def accept(self):
        if self.index.isValid():
            self.index.model().markBetween(self.index,self.startBox.value(),self.endBox.value())
        return super().accept()
    
    
    def startSet(self,value):
        if self.index.isValid():
            self.index.model().setData(self.index,value,details_tree_model.startRole)


    def endSet(self,value):
        if self.index.isValid():
            self.index.model().setData(self.index,value,details_tree_model.endRole)


if __name__ in ['__main__','__console__']:
    d = setBetweenDialog()
    d.show()
