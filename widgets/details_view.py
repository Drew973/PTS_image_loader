# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 10:32:34 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTableView
from image_loader.delegates import checkbox
from PyQt5.QtCore import QSortFilterProxyModel
from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import QItemSelectionModel



class detailsView(QTableView):
    
            
    def __init__(self,parent=None):
        super().__init__(parent)
       # self.checkBoxDelegate = checkbox.checkBoxDelegate(parent=self)
        self.menu = QMenu(self)
        
        fromLayerAct = self.menu.addAction('Select from layer')
        fromLayerAct.triggered.connect(self.selectFromLayer)
        markAct = self.menu.addAction('Mark to load')
        markAct.triggered.connect(self.mark)
        unmarkAct = self.menu.addAction('Unmark to load')
        unmarkAct.triggered.connect(self.unmark)
        dropAct = self.menu.addAction('Remove selected rows')
        dropAct.triggered.connect(self.dropSelected)
        #self.setTextElideMode(Qt.ElideLeft)
        self.setWordWrap(False)

    #model might be proxy model.
    def detailsModel(self):
        if isinstance(self.model(),QSortFilterProxyModel):
            return self.model().sourceModel()
        else:
            return self.model()
        

 #   def edit(self,index,trigger,event):
     #   if index.column() == self.detailsModel().fieldIndex('load'):
    #        return False
     #   
      #  return super().edit(index,trigger,event)


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
        

    def selectFromLayer(self):
        m = self.detailsModel()
        inds = [m.index(r,0) for r in m.selectedFeatureRows()]        
        if isinstance(self.model(),QSortFilterProxyModel):
            inds = [self.model().mapFromSource(i).row() for i in inds]
        self.clearSelection()
        for ind in inds:
            self.selectionModel().select(ind,QItemSelectionModel.Rows|QItemSelectionModel.Select)



    def selectOnLayer(self):
        inds = self.selectionModel().selectedRows()
        if isinstance(self.model(),QSortFilterProxyModel):
            inds = [self.model().mapFromSource(i).row() for i in inds]
        self.detailsModel().selectOnLayer([i.row() for i in inds])


    def unmark(self):
        selected = self.selectionModel().selectedRows(self.detailsModel().fieldIndex('load'))
        
        if isinstance(self.model(),QSortFilterProxyModel):
            selected = [self.model().mapToSource(i) for i in selected]
            
        for i in selected:
            self.detailsModel().setData(i,False)


    def setModel(self,model):
        super().setModel(model)
        #if delegates are not class attributes crashes on model.select(). garbage collection?
      #  self.setItemDelegateForColumn(self.detailsModel().fieldIndex('load'),self.checkBoxDelegate)
        
        for c in ['pk','geom','run']:
            self.setColumnHidden(self.detailsModel().fieldIndex(c),True)

        self.resizeColumnsToContents()
        
        
    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
        
        