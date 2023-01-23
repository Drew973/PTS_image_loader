# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 10:32:34 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTableView,QStyledItemDelegate
from image_loader.delegates import id_delegate#checkbox_delegate,attribute_spin_box_delegate
from PyQt5.QtCore import QSortFilterProxyModel,Qt
from PyQt5.QtWidgets import QMenu



class runsView(QTableView):
    
            
    def __init__(self,parent=None):
        super().__init__(parent)

       # self.checkBoxDelegate = checkbox.checkBoxDelegate(parent=self)
        self.minDelegate = id_delegate.idBoxDelegate(parent=self)
        self.maxDelegate = id_delegate.idBoxDelegate(parent=self)

        self.menu = QMenu(self)
        markAct = self.menu.addAction('Mark to load')     
        markAct.triggered.connect(self.mark)

        unmarkAct = self.menu.addAction('Unmark to load')     
        unmarkAct.triggered.connect(self.unmark)




    #model might be proxy model.
    def runsModel(self):
        if isinstance(self.model(),QSortFilterProxyModel):
            return self.model().sourceModel()
        else:
            return self.model()
        

    def mark(self):
        loadCol = self.runsModel().fieldIndex('load')
        selected = self.selectionModel().selectedRows(loadCol)
        for i in selected:
            self.model().setData(i,True)
        
        
    def unmark(self):
        loadCol = self.runsModel().fieldIndex('load')
        selected = self.selectionModel().selectedRows(loadCol)
        for i in selected:
            self.model().setData(i,False)



    def contextMenuEvent(self, event):
        self.menu.exec_(self.mapToGlobal(event.pos()))
        

    def setModel(self,model):
        #make sure old delegates definitly removed
        
        if self.model() is not None:
            for c in range(self.model().columnCount()):
                self.setItemDelegateForColumn(c,QStyledItemDelegate())
            
            
        super().setModel(model)
        #if delegates are not class attributes crashes on model.select(). garbage collection?
       # self.setItemDelegateForColumn(self.runsModel().fieldIndex('load'),self.checkBoxDelegate)
        self.setItemDelegateForColumn(self.runsModel().fieldIndex('start_id'),self.minDelegate)
        self.setItemDelegateForColumn(self.runsModel().fieldIndex('end_id'),self.maxDelegate)
        self.setSortingEnabled(True)
        self.sortByColumn(self.runsModel().fieldIndex('run'),Qt.AscendingOrder)
        self.setColumnHidden(self.runsModel().fieldIndex('min_id'),True)
        self.setColumnHidden(self.runsModel().fieldIndex('max_id'),True)

