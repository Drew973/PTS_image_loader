# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 13:41:52 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QMenu,QTreeView,QApplication,QShortcut
from image_loader.chainages_dialog import chainagesDialog
from image_loader.mo_difference_dialog import moDifferenceDialog
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


class runsView(QTreeView):
  
    def __init__(self,parent=None):
        super().__init__(parent)
        self.menu = QMenu(self)
        self.chainagesDialog = chainagesDialog(parent=self)
        self.correctionDialog = moDifferenceDialog(parent = self)
        self.setGpsModel(None)
        addRunAct = self.menu.addAction('Add new run...')
        addRunAct.triggered.connect(self.addRun)
        self.findChainageAct = self.menu.addAction('Edit chainage range...')
        self.findChainageAct.triggered.connect(self.setChainage)
        self.findCorrectionAct = self.menu.addAction('Edit correction...')
        self.findCorrectionAct.triggered.connect(self.findCorrection)
        dropRunsAct = self.menu.addAction('Drop selected runs')
        dropRunsAct.triggered.connect(self.dropRuns)
        copyAct = self.menu.addAction('Copy')
        shortcut = QShortcut(QKeySequence.Copy,self,self.copy, context=Qt.WidgetShortcut)
       # copyAct.setShortcut(QKeySequence.Copy)#not triggering
      #  copyAct.setShortcutContext(Qt.WidgetShortcut)
        copyAct.triggered.connect(self.copy)
        
        pasteAct = self.menu.addAction('Paste')
        shortcut = QShortcut(QKeySequence.Paste,self,self.paste, context=Qt.WidgetShortcut)
        pasteAct.triggered.connect(self.paste)
        self.row = -1
        
    def copy(self):
        startFrameCol = self.model().fieldIndex('start_frame')
        endFrameCol = self.model().fieldIndex('end_frame')
        csCol = self.model().fieldIndex('chainage_shift')
        offsetCol = self.model().fieldIndex('offset')
        t = ''
        for ind in self.selectionModel().selectedRows():
            row = ind.row()
            startFrame = self.model().index(row,startFrameCol).data()
            endFrame = self.model().index(row,endFrameCol).data()
            cs = self.model().index(row,csCol).data()
            offset = self.model().index(row,offsetCol).data()
            t += '{sf}\t{ef}\t{cs}\t{of}\n'.format(sf = startFrame , ef = endFrame,cs = cs,of = offset)
        QApplication.clipboard().setText(t)
       
        
    def paste(self):
        t = QApplication.clipboard().text()
        self.model().loadText(t)
        
        
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
      #  self.correctionDialog.setRow(row = self.minSelected())
        self.correctionDialog.setRow(self.row)
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
        for col in range(self.model().columnCount()):
            self.resizeColumnToContents(col)
        
        
    def setGpsModel(self,model):
        self.chainagesDialog.setGpsModel(model)
        self.correctionDialog.gpsModel = model
        
        
    def contextMenuEvent(self, event):
        self.row = self.indexAt(event.pos()).row() #-1 for no index
        
        if self.row == -1:#no run right clicked
            self.findChainageAct.setEnabled(False)
            self.findCorrectionAct.setEnabled(False)
        else:
            self.findChainageAct.setEnabled(True)
            self.findCorrectionAct.setEnabled(True)
        
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
    
    def dropRuns(self):
        self.model().dropRuns(self.selectedPks())

    