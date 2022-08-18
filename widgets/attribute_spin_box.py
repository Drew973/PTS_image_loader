# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 15:55:11 2022

@author: Drew.Bennett



QSpinBox subclass with ability to:
    set value from selected features of layer
    and select features of layer from value


"""

from PyQt5.QtWidgets import QSpinBox,QMenu,QAction

from PyQt5.QtCore import Qt
import logging
logger = logging.getLogger(__name__)


class attributeSpinBox(QSpinBox):
    
    
    def __init__(self,parent=None):
        logger.debug('__init__')
        super().__init__(parent)
        
        
        self.setLayer(None)
        self.setField(None)
        self.setUseMaxSelected(False)
        
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
       
        
        self.fromFeaturesAct = QAction('Set value from selected features',self)
        self.fromFeaturesAct.triggered.connect(self.fromFeatures)
        self.addAction(self.fromFeaturesAct)
        
        
        self.selectFeaturesAct = QAction('Select features on layer',self)
        self.selectFeaturesAct.triggered.connect(self.selectFeatures)
        self.addAction(self.selectFeaturesAct)  

        
       
    def setLayer(self,layer):
        logger.debug('setLayer(%s)',layer)
        self._layer = layer
        
        
        
    def layer(self):
        return self._layer
    
    
    
    def setField(self,field):
        logger.debug('setField(%s)',field)
        self._field = field
        
        
        
    def field(self):
        return self._field


#bool. if True use maximum value when seting value from features, otherwise use minimum. 
    def setUseMaxSelected(self,setUseMaxSelected):
        self._useMax = setUseMaxSelected



    def useMaxSelected(self):
        return self._useMax 
        


    def fromFeatures(self):
        layer = self.layer()
        field = self.field()    
        logger.debug('fromFeatures(). layer = %s, field=%s',layer,field)

        if layer is not None and field is not None:
            
            vals = [f[field] for f in layer.selectedFeatures()]
            if vals:
                if self.useMaxSelected():
                    self.setValue(max(vals))
                else:
                    self.setValue(min(vals))
        
    
    
    def selectFeatures(self):
        layer = self.layer()
        field = self.field()
        logger.debug('selectFeatures(). layer = %s, field=%s',layer,field)

        
        if layer is not None and field is not None:
            e = '"{field}" = {val}'.format(field=field, val=self.value())
            layer.selectByExpression(e)
            
        
    
    
    
    def contextMenuEvent(self, event):
        # QtCore.QTimer.singleShot(0, self.on_timeout)
        super().contextMenuEvent(event)
        menu = self.findChild(QMenu, 'qt_edit_menu')
        if menu is not None:
            print(menu)
