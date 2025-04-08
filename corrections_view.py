# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 10:18:17 2025

@author: Drew.Bennett
"""


from PyQt5.QtWidgets import QTableView , QMenu , QShortcut , QApplication
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

from image_loader import correction_dialog

class correctionsView(QTableView):
    
    
    def __init__(self , parent = None):
        super().__init__(parent = parent)
        self.row = -1
        self.menu = QMenu(self)
        self.addCorrectionAct = self.menu.addAction('Add new correction...')
        self.addCorrectionAct.triggered.connect(self.showAddDialog)
        self.editCorrectionAct = self.menu.addAction('Edit correction...')
        self.editCorrectionAct.triggered.connect(self.showEditDialog)
        self.deleteCorrectionAct = self.menu.addAction('Delete selected corrections')
        self.deleteCorrectionAct.triggered.connect(self.deleteSelected)
        self.correctionDialog = correction_dialog.correctionDialog(parent = self)


        copyAct = self.menu.addAction('Copy')
        shortcut = QShortcut(QKeySequence.Copy,self,self.copy, context=Qt.WidgetShortcut)
        copyAct.triggered.connect(self.copy)
        
        pasteAct = self.menu.addAction('Paste')
        shortcut = QShortcut(QKeySequence.Paste,self,self.paste, context=Qt.WidgetShortcut)
        pasteAct.triggered.connect(self.paste)


    def copy(self):
        if hasattr(self.model(),'copyRows'):
            self.model().copyRows([i.row() for i in self.selectionModel().selectedRows()])
            
    
    
    def paste(self):
        if hasattr(self.model(),'paste'):
            self.model().paste()
        

        
    def setModel(self , model):
        super().setModel(model)
        if hasattr(model,'fieldIndex'):
            self.setColumnHidden(model.fieldIndex('pk'),True)
            self.setColumnHidden(model.fieldIndex('run'),True)
        self.resizeColumnsToContents()
        
        
        
    def contextMenuEvent(self, event):
        self.row = self.indexAt(event.pos()).row() #-1 for no index        
        
        if self.row == -1:#no row right clicked
            self.editCorrectionAct.setEnabled(False)
        else:
            self.editCorrectionAct.setEnabled(True)
        
        self.menu.exec_(self.mapToGlobal(event.pos()))
            
        
        
    def showAddDialog(self):
        self.correctionDialog.setRow(model = self.model() , row = -1)
        self.correctionDialog.show()
        
         
    def showEditDialog(self):
        self.correctionDialog.setRow(model = self.model() , row = self.row)
        self.correctionDialog.show()


    def selectedPks(self):
        return [index.data() for index in self.selectionModel().selectedRows(self.model().fieldIndex('pk'))]


    def deleteSelected(self):
        self.model().drop(self.selectedPks())    
        
        
        