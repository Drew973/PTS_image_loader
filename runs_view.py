# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:41:52 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QMenu,QTreeView#QTableView
#from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog,QFormLayout,QDialogButtonBox,QDoubleSpinBox

#dialog for inserting/updating start and end chainages
#set row to None to insert,integer with runModel row to update

class chainagesDialog(QDialog):
    
    def __init__(self,runsModel=None,gpsModel=None,parent=None):
        self.runsModel = runsModel
        self.setGpsModel(gpsModel)
        self.row = None
        super().__init__(parent=parent)        
        self.setLayout(QFormLayout())
        self.startChainage = QDoubleSpinBox()
        self.endChainage = QDoubleSpinBox()
        self.layout().addRow('start_chainage',self.startChainage)
        self.layout().addRow('end_chainage',self.endChainage)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.layout().addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)


    def setGpsModel(self,model):
        self.gpsModel = model
        if self.gpsModel is not None:
            limits = self.gpsModel.chainageLimits()
            self.startChainage.setRange(limits[0],limits[1])
            self.endChainage.setRange(limits[0],limits[1])


    def setRow(self,row):
        self.row = row
        if row is None:
            self.setWindowTitle('Add run')
        else:
            self.setWindowTitle('Edit chainages for run {run}'.format(run=row+1))
            self.startChainage.setValue(self.runsModel.index(row,self.runsModel.fieldIndex('start_chainage')).data())
            self.endChainage.setValue(self.runsModel.index(row,self.runsModel.fieldIndex('end_chainage')).data())
            
            
    def accept(self):
        if self.runsModel is not None:
            if self.row is None:
                self.runsModel.addRuns([{'start_chainage':self.startChainage.value(),'end_chainage':self.endChainage.value()}])
            else:
                self.runsModel.setData(self.runsModel.index(self.row,self.runsModel.fieldIndex('start_chainage')),self.startChainage.value())                
                self.runsModel.setData(self.runsModel.index(self.row,self.runsModel.fieldIndex('end_chainage')),self.endChainage.value())
        return super().accept()




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
        
        self.chainagesDialog = chainagesDialog()
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