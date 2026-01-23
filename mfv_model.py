# -*- coding: utf-8 -*-
"""
Created on Thu Dec 11 08:35:39 2025

@author: Drew.Bennett

mypy mfv_model.py --follow-imports=silent
"""



from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from image_loader.db_functions import runQuery





class mfvModel(QSqlTableModel):
    
    def __init__(self,db:QSqlDatabase , parent:QWidget|None = None):
        super().__init__(parent,db)
        self.setTable('mfv')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setSort(self.fieldIndex('mfv_ref') , Qt.AscendingOrder)
        self.select()
        
        
        
    #raise error if fails due to unique constraint etc.
    def insertMfv(self, mfvRef: str):
        print(mfvRef)
        runQuery('insert into mfv(mfv_ref) values (:mfv)',values = {':mfv':mfvRef} , db = self.database())
        self.select()
        
    
    def dropMfv(self,mfvRef:str):
        runQuery('delete from mfv where mfv_ref = :mfv',values = {':mfv':mfvRef} , db = self.database())
        self.select()
        
        
    def dropAllMfv(self):
        runQuery('delete from mfv', db = self.database())
        self.select()     
        
        
    def allMfvs(self) -> list[str]:
        mfvs = []
        col:int = self.fieldIndex('mfv_ref')
        for row in range(self.rowCount()):
            mfvs.append(self.index(row,col).data())
        return mfvs
            
        