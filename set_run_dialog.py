# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 14:02:44 2023

@author: Drew.Bennett
"""
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QComboBox,QDialogButtonBox


class setRunDialog(QDialog):
    
    def __init__(self,runsModel,model,parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.runBox = QComboBox(self)
        self.layout().addWidget(self.runBox)
        self.runBox.setModel(runsModel)
        self.runBox.setEditable(True)
        self.model = model
        self.indexes = []
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.layout().addWidget(self.buttons)
        self.buttons.rejected.connect(self.reject)
        self.buttons.accepted.connect(self.accept)


    def setIndexes(self,indexes):
        self.indexes = indexes
        
        
    def accept(self):
        self.model.setRunForItems(self.indexes,self.runBox.currentText())
        return super().accept()