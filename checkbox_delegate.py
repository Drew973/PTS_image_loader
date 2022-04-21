# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 12:42:34 2022

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtWidgets import QCheckBox


class checkBoxDelegate(QStyledItemDelegate):
    
    def createEditor(self,parent,option,index):
        editor = QCheckBox(parent)
        editor.setStyleSheet('QCheckBox { background-color: white }')
        return editor
       
    
    
    def setEditorData(self,editor,index):
        editor.setChecked(bool(index.data()))
        
        
  #  def setModelData(self,editor,model,index):
  #      model.setData(index)