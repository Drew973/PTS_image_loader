# -*- coding: utf-8 -*-


from PyQt5.QtWidgets import QStyledItemDelegate

from image_loader.widgets import attribute_spin_box
    
    
    

class attributeSpinBoxDelegate(QStyledItemDelegate):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)

        self.setLayer(None)
        self.setField(None)
        self.setUseMaxSelected(False)

 
    def setLayer(self,layer):
        self._layer = layer
        
        
    def layer(self):
        return self._layer
    
    
    
    def field(self):
        return self._field
    
    
    def setField(self,field):
        self._field = field
    
        
    
#bool. if True use maximum value when seting value from features, otherwise use minimum. 
    def setUseMaxSelected(self,setUseMaxSelected):
        self._useMax = setUseMaxSelected


    def useMaxSelected(self):
        return self._useMax
    
    
    
    def createEditor(self,parent,option,index):
        w = attribute_spin_box.attributeSpinBox(parent)
        w.setLayer(self.layer())
        w.setField(self.field())
        w.setUseMaxSelected(self.useMaxSelected())
        w.setMaximum(9999)
        return w
    