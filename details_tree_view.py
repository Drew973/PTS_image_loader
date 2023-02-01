# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 08:04:05 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QMenu,QAbstractItemView
from PyQt5.QtCore import QModelIndex


from image_loader.details_tree_model import cols
from image_loader.set_between_dialog import setBetweenDialog

class detailsTreeView(QTreeView):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.contextRun = QModelIndex()
        
        self.markBetweenDialog = setBetweenDialog()
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.detailMenu = QMenu(self)

        markAct = self.detailMenu.addAction('Mark to load')     
        markAct.triggered.connect(self.mark)

        unmarkAct = self.detailMenu.addAction('Unmark to load')     
        unmarkAct.triggered.connect(self.unmark)
    
        dropAct = self.detailMenu.addAction('Remove')
        dropAct.triggered.connect(self.dropSelected)
    
        self.runsMenu = QMenu(self)
        markBetweenAct = self.runsMenu.addAction('Mark between...')     
        markBetweenAct.triggered.connect(self.showMarkBetweenDialog)
    
        markRunAct = self.runsMenu.addAction('Mark all in run')     
        markRunAct.triggered.connect(self.markRun)
    
        unmarkRunAct = self.runsMenu.addAction('Unmark all in run')     
        unmarkRunAct.triggered.connect(self.unMarkRun)
    
    
    
    def contextMenuEvent(self, event):
        
        index = self.indexAt(event.pos())#index that was right clicked
        if index.isValid():

            if self.model().indexIsDetail(index):
                self.detailMenu.exec_(self.mapToGlobal(event.pos()))
                self.contextRun = QModelIndex()
            
            
            if self.model().indexIsRun(index):
                self.contextRun = index
                self.runsMenu.exec_(self.mapToGlobal(event.pos()))


    def dropSelected(self):
        self.model().dropDetails(self.selectionModel().selectedRows(2))



    def mark(self):
        loadCol = cols['load']

        for i in self.selectionModel().selectedRows(loadCol):
            if self.model().indexIsDetail(i):
                self.model().setData(i,True)
    
    
    #mark all in run
    def markRun(self):
        self.model().markRun(self.contextRun)
    
    
    #unmark all in run
    def unMarkRun(self):
        self.model().unMarkRun(self.contextRun)
    
    #unmark selected details
    def unmark(self):
        loadCol = cols['load']
        
        for i in self.selectionModel().selectedRows(loadCol):
            if self.model().indexIsDetail(i):
                self.model().setData(i,False)


    def showMarkBetweenDialog(self):
        self.markBetweenDialog.setIndex(self.contextRun)
        self.markBetweenDialog.open()

    
    #mark run betwwen ids
    def markBetween(self):
        pass
        
    