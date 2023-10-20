# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:41:52 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QMenu,QTreeView#QTableView
from image_loader.chainages_dialog import chainagesDialog


class runsView(QTreeView):
  
    def __init__(self,parent=None):
        super().__init__(parent)
        self.menu = QMenu(self)
        
        addRunAct = self.menu.addAction('Add new run...')
        addRunAct.triggered.connect(self.addRun)
        
        findChainageAct = self.menu.addAction('Find chainage range...')
        findChainageAct.triggered.connect(self.setChainage)
        
        findCorrectionAct = self.menu.addAction('Find correction...')
        findCorrectionAct.triggered.connect(self.findCorrection)
        
        dropRunsAct = self.menu.addAction('Drop run')
        dropRunsAct.triggered.connect(self.dropRuns)
        
        self.chainagesDialog = chainagesDialog(parent=self)
        self.setGpsModel(None)

        
    def addRun(self):
        self.chainagesDialog.setRow(None)
        self.chainagesDialog.show()
        
    
    def setChainage(self):
        row = min([index.row() for index in self.selectionModel().selectedRows(self.model().fieldIndex('pk'))])
        self.chainagesDialog.setRow(row)
        self.chainagesDialog.show()
        
        
    def setModel(self,model):
        super().setModel(model)        
        self.chainagesDialog.runsModel = model
        if hasattr(model,'fieldIndex'):
            self.setColumnHidden(model.fieldIndex('pk'),True)
        
        
    def setGpsModel(self,model):
        self.chainagesDialog.setGpsModel(model)
        
        
    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
    
    def dropRuns(self):
        pks = [index.data() for index in self.selectionModel().selectedRows(self.model().fieldIndex('pk'))]
   #     print(pks)
        self.model().dropRuns(pks)

    
    def findCorrection(self):
        pass