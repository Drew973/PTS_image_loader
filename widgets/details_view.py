# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 10:32:34 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTableView
from image_loader.delegates import checkbox

import logging
logger = logging.getLogger(__name__)

from PyQt5.QtCore import QSortFilterProxyModel,Qt
from PyQt5.QtWidgets import QMenu



class detailsView(QTableView):
    
            
    def __init__(self,parent=None):
        super().__init__(parent)
        self.checkBoxDelegate = checkbox.checkBoxDelegate(parent=self)
        self.menu = QMenu(self)
        markAct = self.menu.addAction('Mark to load')
        markAct.triggered.connect(self.mark)
        unmarkAct = self.menu.addAction('Unmark to load')
        unmarkAct.triggered.connect(self.unmark)
        dropAct = self.menu.addAction('Remove selected rows')
        dropAct.triggered.connect(self.dropSelected)

    #model might be proxy model.
    def detailsModel(self):
        if isinstance(self.model(),QSortFilterProxyModel):
            return self.model().sourceModel()
        else:
            return self.model()
        

#all selected rows are in details model
    def mark(self):
        selected = self.selectionModel().selectedRows(self.detailsModel().fieldIndex('load'))
        
        if isinstance(self.model(),QSortFilterProxyModel):
            selected = [self.model().mapToSource(i) for i in selected]
            
        for i in selected:
            self.detailsModel().setData(i,True)


    def selectedPks(self):
        return [i.data() for i in self.selectionModel().selectedRows(self.detailsModel().fieldIndex('pk'))]
       

    def dropSelected(self):
        self.detailsModel().drop(self.selectedPks())
        self.detailsModel().select()
        

    def unmark(self):
        selected = self.selectionModel().selectedRows(self.detailsModel().fieldIndex('load'))
        
        if isinstance(self.model(),QSortFilterProxyModel):
            selected = [self.model().mapToSource(i) for i in selected]
            
        for i in selected:
            self.detailsModel().setData(i,False)


    def setModel(self,model):
        logging.debug('setModel')
        super().setModel(model)
        #if delegates are not class attributes crashes on model.select(). garbage collection?
        self.setItemDelegateForColumn(self.detailsModel().fieldIndex('load'),self.checkBoxDelegate)
        
        for c in ['pk','geom','run']:
            self.setColumnHidden(self.detailsModel().fieldIndex(c),True)

        self.resizeColumnsToContents()
        
        
    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
        
        
   
        
        