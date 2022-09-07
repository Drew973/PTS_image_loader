# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 10:32:34 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTableView
from image_loader.delegates import checkbox,id_delegate#checkbox_delegate,attribute_spin_box_delegate

import logging
logger = logging.getLogger(__name__)

from PyQt5.QtCore import QSortFilterProxyModel,Qt



class runsView(QTableView):
    
            
    def __init__(self,parent=None):
        super().__init__(parent)

        self.checkBoxDelegate = checkbox.checkBoxDelegate(parent=self)
        self.minDelegate = id_delegate.idBoxDelegate(parent=self)
        self.maxDelegate = id_delegate.idBoxDelegate(parent=self)

     

    #model might be proxy model.
    def runsModel(self):
        if isinstance(self.model(),QSortFilterProxyModel):
            return self.model().sourceModel()
        else:
            return self.model()
        


    def setModel(self,model):
        logging.debug('setModel')
        super().setModel(model)

        #if delegates are not class attributes crashes on model.select(). garbage collection?
        self.setItemDelegateForColumn(self.runsModel().fieldIndex('load'),self.checkBoxDelegate)
        self.setItemDelegateForColumn(self.runsModel().fieldIndex('start_id'),self.minDelegate)
        self.setItemDelegateForColumn(self.runsModel().fieldIndex('end_id'),self.maxDelegate)
        self.setSortingEnabled(True)
        self.sortByColumn(self.runsModel().fieldIndex('run'),Qt.AscendingOrder)
        self.setColumnHidden(self.runsModel().fieldIndex('min_id'),True)
        self.setColumnHidden(self.runsModel().fieldIndex('max_id'),True)

