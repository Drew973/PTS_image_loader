# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 10:17:58 2023

@author: Drew.Bennett
"""


from PyQt5.QtWidgets import QDialog,QComboBox,QDialogButtonBox,QHBoxLayout




class comboBoxDialog(QDialog):
    
    def __init__(self,parent = None,box = None):    
        super().__init__(parent=parent)
        self.setLayout(QHBoxLayout())

        if box is None:
            self.box = QComboBox()
            self.layout().addWidget(self.box)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addWidget(buttons)
        
        

def chooseItem(items,title = 'choose item...'):
    d = comboBoxDialog()
    d.box.addItems([str(item) for item in items])
    d.setWindowTitle(title)
    r = d.exec_()
    if r == QDialog.Accepted:
        i = d.box.currentIndex()
        if i !=-1:
            return items[i]
    
    
if __name__ in ('__main__','__console__'):
   # d = comboBoxDialog()
   # d.show()
    item = chooseItem(['a','b',2])
    print(item)
    