# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 10:20:47 2022

@author: Drew.Bennett
"""


from PyQt5.QtSql import QSqlDatabase,QSqlQuery,QSqlQueryModel



from PyQt5.QtWidgets import QComboBox,QDialog,QFormLayout,QSpinBox,QDialogButtonBox


'''
    dialog to select all images between start and end in run.
'''

class selectDialog(QDialog):
        
    def __init__(self,parent=None):
        
        super().__init__(parent)
        self.setLayout(QFormLayout(self))
        self.model = QSqlQueryModel(self)
        self.runBox = QComboBox(self)
        self.runBox.setModel(self.model)
        self.runBox.currentIndexChanged.connect(self.runChanged)
        self.layout().addRow('run',self.runBox)
        self.minBox= QSpinBox(self)
        self.layout().addRow('start',self.minBox)
        self.maxBox= QSpinBox(self)
        self.layout().addRow('end',self.maxBox)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,parent=self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout().addRow(self.buttonBox)
        self.setImageModel(None)
        
        
    def setImageModel(self,model):
        self._imageModel = model
        
        
    def imageModel(self):
        return self._imageModel 


    #refresh model.
    def select(self):
        self.model.setQuery(QSqlQuery('select run,min(image_id),max(image_id) from details group by run',QSqlDatabase.database('image_loader')))
        self.runChanged(self.runBox.currentIndex())


    def runChanged(self,row):
        self.minBox.setMinimum(self.model.index(row,1).data())
        self.maxBox.setMinimum(self.model.index(row,1).data())
        self.minBox.setMaximum(self.model.index(row,2).data())
        self.maxBox.setMaximum(self.model.index(row,2).data())


    def accept(self):
        if self.imageModel() is not None:
            self.imageModel().selectRun(run=self.runBox.currentText(),start=self.minBox.value(),end=self.maxBox.value())
        super().accept()


if __name__=='__console__':
    d = selectDialog()
    d.select()
    d.show()
  