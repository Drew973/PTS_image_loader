# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QStyledItemDelegate

import logging
logger = logging.getLogger(__name__)

from image_loader.widgets import image_id_box

'''
    delegate with SpinBox.
    spinbox has maximum value of model.maxValue(index)
    and minimum of model.minValue(index)
'''
    
from PyQt5.QtCore import QSortFilterProxyModel
    

class idBoxDelegate(QStyledItemDelegate):
        

    def createEditor(self,parent,option,index):
        logger.debug('createEditor')
        w = image_id_box.imageIdBox(parent)
        
        #get index of source model if necessary.
        if isinstance(index.model(),QSortFilterProxyModel):
            index = index.model().mapToSource(index)
            
        w.setIndex(index)
        
        return w
