# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 15:41:24 2022

@author: Drew.Bennett
"""

from qgis.gui import QgsMapLayerComboBox,QgsFieldComboBox



'''
if parent is QgsMapLayerComboBox sets layer to parent's layer and connects layerChanged signal to setLayer slot.

tries to set field to default when layer set.
'''

class fieldBox(QgsFieldComboBox):
    
    def __init__(self,parent=None,default=''):
        
        super().__init__(parent)
        self.default = default
        self.setAllowEmptyFieldName(True)

        if isinstance(parent,QgsMapLayerComboBox):
            parent.layerChanged.connect(self.setLayer)
            self.setLayer(parent.currentLayer())
            
        
    def setLayer(self,layer):
        super().setLayer(layer)
        i = self.findText(self.default)#-1 if not found
        if i !=-1:
            self.setCurrentIndex(i)
        
if __name__ == '__console__':
    b = QgsMapLayerComboBox()
    b.show()

    c = fieldBox(b,default='sec')

    c.show()
