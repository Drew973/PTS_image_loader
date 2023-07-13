# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 12:16:57 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTableView,QMenu
from image_loader.correction_dialog import correctionDialog
from PyQt5.QtCore import QModelIndex



class correctionsView(QTableView):
  
    def __init__(self,parent=None):
        super().__init__(parent)
        self.correctionDialog = correctionDialog(parent=self)
        self.correctionDialog.hide()
        self.menu = QMenu(self)
        dropAct = self.menu.addAction('Remove selected rows')
        dropAct.triggered.connect(self.dropSelected)
        addAct = self.menu.addAction('Add correction...')
        addAct.triggered.connect(self.add)
        #self.setWordWrap(False)        
        self.doubleClicked.connect(self.editSelected)
        
        
    def close(self):
        self.correctionDialog.close()
        return super().close()
    
    
    def setModel(self,model):
        super().setModel(model)
        self.correctionDialog.setModel(model)
        toShow = [model.fieldIndex('chainage'),model.fieldIndex('x'),model.fieldIndex('y')]
        for c in range(model.columnCount()):
            self.setColumnHidden(c,not c in toShow)
    
    
    def editSelected(self,index=None):
        self.correctionDialog.setIndex(index)
        self.correctionDialog.setWindowTitle('Edit correction')
        self.correctionDialog.show()
      #  self.correctionDialog.showMarkers()
        
        
    def add(self):
        self.correctionDialog.setIndex(QModelIndex())
        self.correctionDialog.setWindowTitle('Add correction')
        self.correctionDialog.show()
   #     self.correctionDialog.showMarkers()
        
    def selected(self):
        return self.selectionModel().selectedRows(self.detailsModel().fieldIndex('pk'))
        
  
    def dropSelected(self):
        if self.model():
            self.model().dropRows(self.selectionModel().selectedRows(self.model().fieldIndex('pk')))
    
        
    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
