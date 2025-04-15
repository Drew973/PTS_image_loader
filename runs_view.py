# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:41:52 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QMenu,QTreeView,QApplication,QShortcut
from image_loader.edit_run_dialog import chainagesDialog
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt , QItemSelectionModel



class runsView(QTreeView):
  
    def __init__(self,parent=None):
        super().__init__(parent)
        self.menu = QMenu(self)
        self.chainagesDialog = chainagesDialog(parent=self)
        self.setGpsModel(None)
        addRunAct = self.menu.addAction('Add new run...')
        addRunAct.triggered.connect(self.addRun)
        self.findChainageAct = self.menu.addAction('Edit chainage range...')
        self.findChainageAct.triggered.connect(self.setChainage)
        dropRunsAct = self.menu.addAction('Drop selected runs')
        dropRunsAct.triggered.connect(self.dropRuns)
        copyAct = self.menu.addAction('Copy')
        shortcut = QShortcut(QKeySequence.Copy,self,self.copy, context=Qt.WidgetShortcut)
        copyAct.triggered.connect(self.copy)
        
        pasteAct = self.menu.addAction('Paste')
        shortcut = QShortcut(QKeySequence.Paste,self,self.paste, context=Qt.WidgetShortcut)
        pasteAct.triggered.connect(self.paste)
        self.row = -1
        
        
    def copy(self):
        startFrameCol = self.model().fieldIndex('start_frame')
        endFrameCol = self.model().fieldIndex('end_frame')
   
        t = ''
        for ind in self.selectionModel().selectedRows():
            row = ind.row()
            startFrame = self.model().index(row,startFrameCol).data()
            endFrame = self.model().index(row,endFrameCol).data()
            t += '{sf}\t{ef}\n'.format(sf = startFrame , ef = endFrame)
        QApplication.clipboard().setText(t)
       
        
    def paste(self):
        t = QApplication.clipboard().text()
        self.model().paste(t)
        
        
    def addRun(self):
        self.chainagesDialog.setRow(None)
        self.chainagesDialog.show()
        
        
    #mimimum selected row in tableview
    def minSelected(self) -> int:
        selected = [index.row() for index in self.selectionModel().selectedRows(self.model().fieldIndex('pk'))]
        if selected:
            return min(selected)
        return -1


    def selectedPks(self):
        return [index.data() for index in self.selectionModel().selectedRows(self.model().fieldIndex('pk'))]


    def setChainage(self):
        self.chainagesDialog.setRow(self.minSelected())
        self.chainagesDialog.show()
        
        
    def setModel(self,model):
        super().setModel(model)
        self.chainagesDialog.runsModel = model
        show = ['number','start_frame','end_frame','chainage_shift','offset']
        if hasattr(model,'fieldName'):
            for c in range(model.columnCount()):
                name = model.fieldName(c)
                self.setColumnHidden(c,not name in show)
        for col in range(self.model().columnCount()):
            self.resizeColumnToContents(col)
        
    
    
    #select row and deselect everything else
    def selectRow(self , row:int):        
        flags = QItemSelectionModel.Rows | QItemSelectionModel.ClearAndSelect
        self.selectionModel().select(self.model().index(row,0) , flags)

        
        
        
    def setGpsModel(self,model):
        self.chainagesDialog.setGpsModel(model)
        
        
    def contextMenuEvent(self, event):
        self.row = self.indexAt(event.pos()).row() #-1 for no index
        
        if self.row == -1:#no run right clicked
            self.findChainageAct.setEnabled(False)
        else:
            self.findChainageAct.setEnabled(True)
        
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
    
    def dropRuns(self):
        self.model().dropRuns(self.selectedPks())

    