# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:41:52 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QMenu,QTreeView#QTableView
from image_loader.chainages_dialog import chainagesDialog
from image_loader.mo_difference_dialog import moDifferenceDialog


class runsView(QTreeView):
  
    def __init__(self,parent=None):
        super().__init__(parent)
        self.menu = QMenu(self)
        self.chainagesDialog = chainagesDialog(parent=self)
        self.correctionDialog = moDifferenceDialog(parent = self)
        self.setGpsModel(None)
        addRunAct = self.menu.addAction('Add new run...')
        addRunAct.triggered.connect(self.addRun)
        findChainageAct = self.menu.addAction('Find chainage range...')
        findChainageAct.triggered.connect(self.setChainage)
        findCorrectionAct = self.menu.addAction('Find correction...')
        findCorrectionAct.triggered.connect(self.findCorrection)
        dropRunsAct = self.menu.addAction('Drop run')
        dropRunsAct.triggered.connect(self.dropRuns)

        
    def addRun(self):
        self.chainagesDialog.setRow(None)
        self.chainagesDialog.show()
        
    #->int
    def minSelected(self):
        selected = [index.row() for index in self.selectionModel().selectedRows(self.model().fieldIndex('pk'))]
        if selected:
            return min(selected)
        return -1


    def selectedPks(self):
        return [index.data() for index in self.selectionModel().selectedRows(self.model().fieldIndex('pk'))]



    def setChainage(self):
        self.chainagesDialog.setRow(self.minSelected())
        self.chainagesDialog.show()
        
        
    def findCorrection(self):
        self.correctionDialog.setRow(row = self.minSelected())
        self.correctionDialog.show()
    
        
    def setModel(self,model):
        super().setModel(model)        
        self.chainagesDialog.runsModel = model
        show = ['number','start_frame','end_frame','chainage_shift','offset']
        if hasattr(model,'fieldName'):
            for c in range(model.columnCount()):
                name = model.fieldName(c)
                self.setColumnHidden(c,not name in show)
        self.correctionDialog.setModel(self.model())
        
        
    def setGpsModel(self,model):
        self.chainagesDialog.setGpsModel(model)
        self.correctionDialog.gpsModel = model
        
        
    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
    
    def dropRuns(self):
        self.model().dropRuns(self.selectedPks())

    