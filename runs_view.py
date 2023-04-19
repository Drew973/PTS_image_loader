# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 10:44:07 2023

@author: Drew.Bennett
"""


from PyQt5.QtWidgets import QTableView,QMenu,QApplication
from image_loader.set_between_dialog import setBetweenDialog
from PyQt5.QtCore import Qt


class runsView(QTableView):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.markBetweenDialog = setBetweenDialog()
        self.runsMenu = QMenu(self)
        markBetweenAct = self.runsMenu.addAction('Mark between...')     
        markBetweenAct.triggered.connect(self.showMarkBetweenDialog)
        markRunAct = self.runsMenu.addAction('Mark all in run')     
        markRunAct.triggered.connect(self.markRuns)
        
        markStartAct = self.runsMenu.addAction('Mark start of run')     
        markStartAct.triggered.connect(self.markStart)
        
        unmarkRunAct = self.runsMenu.addAction('Unmark all in run')     
        unmarkRunAct.triggered.connect(self.unMarkRun)
        
      #  self.copyAct = self.runsMenu.addAction('Copy')
    #    self.copyAct.triggered.connect(self.copy)
        self.setContextMenuPolicy(Qt.CustomContextMenu)


    def setModel(self,model):
        super().setModel(model)
        self.hideCols()
                    
    
    def hideCols(self):
        if hasattr(self.model(),'cols'):
            cols = self.model().cols
            toShow = [cols.run,cols.chainageCorrection,cols.offsetCorrection]
            for c in range(self.model().columnCount()):
                self.setColumnHidden(c,not c in toShow)

    
    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())#index that was right clicked
        if index.isValid():
            self.markBetweenDialog.setIndex(index)
            self.runsMenu.exec_(self.mapToGlobal(event.pos()))




    #mark all in run
    def markRuns(self):
        self.model().markRuns(self.selectionModel().selectedRows(self.model().cols.run),value=True)
    
    
    def markStart(self):
        self.model().markStarts(self.selectionModel().selectedRows(self.model().cols.run))
        
    
    #unmark all in run
    def unMarkRun(self):
        self.model().markRuns(self.selectionModel().selectedRows(self.model().cols.run),value=False)
    

    def showMarkBetweenDialog(self):
        self.selectionModel().selectedRows(self.model().cols.run)
        self.markBetweenDialog.open()

    
    #mark run betwwen ids
    def markBetween(self):
        pass
        
        
    def copy(self):  
        data = {}
        cols = self.model().columnCount()
        for index in self.selectionModel().selectedIndexes():
            row = index.row()
            if not row in data:
                data[index.row()] = [''] * cols
            data[row][index.column()] = str(index.data())
        #print(data)
        r = '\n'.join(['\t'.join(data[k]) for k in data])
        #print(r)
        QApplication.clipboard().setText(r)            