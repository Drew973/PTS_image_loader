# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:12:37 2023

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
from image_loader.db_functions import runQuery,defaultDb



class runsTableModel(QSqlTableModel):
    
    def __init__(self,db=None,parent=None):
        if db is None:
            db = defaultDb()
        super().__init__(parent,db)
        self.setTable('runs')
        self.select()
        self.setSort(0,Qt.AscendingOrder)
        
        
    #[int]
    def addRuns(self,runs):
        db = self.database()
        db.transaction()
        
        for n in runs:
            runQuery(query = 'insert into runs(number) values (:n) on conflict IGNORE',db=db,values = {':n':n})
            
        db.commit()
        