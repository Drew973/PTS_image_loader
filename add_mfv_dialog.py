# -*- coding: utf-8 -*-
"""
Created on Wed Jan  7 12:33:08 2026

@author: Drew.Bennett

dialog with line edit.
mypy add_mfv_dialog.py --follow-imports=silent
"""

from PyQt5.QtWidgets import QDialog,QFormLayout,QDialogButtonBox,QLineEdit,QWidget

class addMfvDialog(QDialog):
    
    def __init__(self, parent:QWidget|None = None):
        super().__init__(parent=parent)
      #  self.setWindowModality(Qt.WindowModal)
        layout = QFormLayout()
        
        self.mfvBox = QLineEdit()
        layout.addRow('MFV number',self.mfvBox)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        layout.addRow(buttons)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.setLayout(layout)
        
        
    def getMfv(self) -> str:
          return self.mfvBox.text()