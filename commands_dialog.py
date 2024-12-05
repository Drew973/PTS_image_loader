# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 13:38:48 2024

@author: Drew.Bennett
"""

#from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog,QVBoxLayout,QDialogButtonBox,QProgressBar,QListWidget
from PyQt5.QtCore import pyqtSignal


class commandsDialog(QDialog):
    
    canceled = pyqtSignal()
    
    def __init__(self,parent=None,title:str = 'Processing'):
        super().__init__(parent)
        self.canceledValue = False
        self.setLayout(QVBoxLayout())

        self.progressBar = QProgressBar()
        self.layout().addWidget(self.progressBar)
        
        self.resultsBox = QListWidget()
        self.resultsBox.setToolTip('Errors')
        self.layout().addWidget(self.resultsBox)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
     #   buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
       # buttons.closed.connect(self.close)
        self.layout().addWidget(buttons)
        self.setLabelText(title)

    
    def setLabelText(self,text:str):
        self.setWindowTitle(text)
        
    def setValue(self,value:int):
        self.progressBar.setValue(value)
        
        
    def value(self):
        return self.progressBar.value()
        
        
    def wasCanceled(self):
        return self.canceledValue
    
    
    def setRange(self,minimum:int,maximum:int):
        self.progressBar.setRange(minimum,maximum)
    
    
    def commandCompleted(self,i:int,command:str,result:str):
      #  print('{c} : {r}'.format(c = command,r = result))
        if result != '':
            self.resultsBox.addItem('{c} : {r}'.format(c = command,r = result))
        if self.progressBar.value() == self.progressBar.maximum():
            if self.resultsBox.count() == 0:
                self.resultsBox.addItem('completed with no errors')
                self.close()
            

    def accept(self):
        self.canceled.emit()
        super().accept()
        
        
    def reject(self):
        self.canceled.emit()
        super().reject()
    
    
    def close(self):
        self.reject()
        super().close()
    
if __name__ in ('__main__','__console__'):
    d = commandsDialog()
    d.exec()    
    