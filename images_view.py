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
       # self.checkBoxDelegate = checkbox.checkBoxDelegate(parent=self)
        self.menu = QMenu(self)
     #   fromLayerAct = self.menu.addAction('Select from layer')
      #  fromLayerAct.triggered.connect(self.selectFromLayer)
        markAct = self.menu.addAction('Mark selected rows')
        markAct.triggered.connect(self.mark)
        unmarkAct = self.menu.addAction('Unmark selected rows')
        unmarkAct.triggered.connect(self.unmark)
        dropAct = self.menu.addAction('Remove selected rows')
        dropAct.triggered.connect(self.dropSelected)
        #self.setTextElideMode(Qt.ElideLeft)
        self.setWordWrap(False)        
  
    
    #def setModel(self,model):
   #     super().setModel(model)
   #     self.hideCols()
   
    def hideCols(self):
        if hasattr(self.model(),'cols'):
            cols = self.model().cols
            toShow = [cols.load,cols.imageId,cols.file,cols.georeferenced]
            for c in range(self.model().columnCount()):
                self.setColumnHidden(c,not c in toShow)
              #  print(c,not c in toShow)
              
              
#all selected rows are in details model
    def mark(self):
        if self.detailsModel():
            selected = self.selectionModel().selectedRows(self.detailsModel().cols.load)
            
            if isinstance(self.model(),QSortFilterProxyModel):
                selected = [self.model().mapToSource(i) for i in selected]
                
            for i in selected:
                self.detailsModel().setData(i,True)


  
    def dropSelected(self):
        if self.detailsModel():
            rows = [i.row() for i in self.selectionModel().selectedRows(self.detailsModel().cols.run)]
            self.detailsModel().dropRows(rows)
    


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


    def unmark(self):
        if self.detailsModel():
            selected = self.selectionModel().selectedRows(self.detailsModel().cols.load)
            if isinstance(self.model(),QSortFilterProxyModel):
                selected = [self.model().mapToSource(i) for i in selected]
            for i in selected:
                self.detailsModel().setData(i,False)

        
    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
    #model might be proxy model.
    def detailsModel(self):
        if isinstance(self.model(),QSortFilterProxyModel):
            return self.model().sourceModel()
        else:
            return self.model()                      
              
      
              