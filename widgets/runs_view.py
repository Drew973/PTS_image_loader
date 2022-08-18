# -*- coding: utf-8 -*-
"""
Created on Wed Jun  8 10:32:34 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QTableView
from image_loader.delegates import attribute_spin_box_delegate,checkbox#checkbox_delegate

import logging
logger = logging.getLogger(__name__)



class runsView(QTableView):
    
            
    def __init__(self,parent=None):
        super().__init__(parent)

        self.checkBoxDelegate = checkbox.checkBoxDelegate(parent=self)

        self.maxDelegate = attribute_spin_box_delegate.attributeSpinBoxDelegate()
        self.maxDelegate.setUseMaxSelected(True)
        
        self.minDelegate = attribute_spin_box_delegate.attributeSpinBoxDelegate()

      #  self.setField(None)
       # self.setLayer(None)
    
    
    
    def setLayer(self,layer):
        logger.debug('setLayer(%s)',layer)
        self._layer = layer         
        self.maxDelegate.setLayer(layer)
        self.minDelegate.setLayer(layer)

    
         
    def setField(self,field):
        logger.debug('setField(%s)',field)
        self.minDelegate.setField(field)
        self.maxDelegate.setField(field)

    

    def setModel(self,model):
        logging.debug('setModel')
        super().setModel(model)
        
        #if delegates are not class attributes crashes on model.select(). garbage collection?

        self.setItemDelegateForColumn(model.fieldIndex('show'),self.checkBoxDelegate)
        self.setItemDelegateForColumn(model.fieldIndex('start_id'),self.minDelegate)
        self.setItemDelegateForColumn(model.fieldIndex('end_id'),self.maxDelegate)
