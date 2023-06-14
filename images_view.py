# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 12:16:57 2023

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTableView,QMenu
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtCore import QItemSelectionModel


class imagesView(QTableView):
  
    def __init__(self,parent=None):
        super().__init__(parent)
        self.menu = QMenu(self)
        markAct = self.menu.addAction('Mark selected rows')
        markAct.triggered.connect(self.mark)
        unmarkAct = self.menu.addAction('Unmark selected rows')
        unmarkAct.triggered.connect(self.unmark)
        dropAct = self.menu.addAction('Remove selected rows')
        dropAct.triggered.connect(self.dropSelected)
        self.setWordWrap(False)        
        
    
    def setModel(self,model):
        super().setModel(model)
        
        toShow = [model.fieldIndex('marked'),model.fieldIndex('image_id'),model.fieldIndex('original_file'),model.fieldIndex('image_type')]
        for c in range(model.columnCount()):
            self.setColumnHidden(c,not c in toShow)
        

         
    def selected(self):
        return self.selectionModel().selectedRows(self.detailsModel().fieldIndex('pk'))
        
       
    #triggered emits bool
    def _mark(self,value=True):
        if self.detailsModel():
            selected = self.selectionModel().selectedRows(self.detailsModel().fieldIndex('marked'))
            
            if isinstance(self.model(),QSortFilterProxyModel):
                selected = [self.model().mapToSource(i) for i in selected]
                
                
            self.detailsModel().mark(indexes = selected, value = value)
          
            
    def mark(self):
        self._mark(value=True)

    def unmark(self):
        self._mark(value=False)
        
        
        
  
    def dropSelected(self):
        if self.detailsModel():
            self.detailsModel().dropRows(self.selectionModel().selectedRows(self.detailsModel().fieldIndex('pk')))
    


    def selectFromLayer(self):
        m = self.detailsModel()
        
        if m:
            inds = [m.index(r,0) for r in m.selectedFeatureRows()]        
            if isinstance(self.model(),QSortFilterProxyModel):
                inds = [self.model().mapFromSource(i).row() for i in inds]
            self.clearSelection()
            for ind in inds:
                self.selectionModel().select(ind,QItemSelectionModel.Rows|QItemSelectionModel.Select)



    def selectOnLayer(self):
        if self.detailsModel():
            inds = self.selectionModel().selectedRows()
            if isinstance(self.model(),QSortFilterProxyModel):
                inds = [self.model().mapFromSource(i).row() for i in inds]
            self.detailsModel().selectOnLayer([i.row() for i in inds])



        
    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
    #model might be proxy model.
    def detailsModel(self):
        if isinstance(self.model(),QSortFilterProxyModel):
            return self.model().sourceModel()
        else:
            return self.model()                      
              
      
              