# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 15:42:30 2026

@author: Drew.Bennett
"""

from PyQt5.QtCore import QModelIndex


from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableView
from PyQt5.QtSql import QSqlDatabase

from image_loader.db_functions import runQuery,defaultDb



COLS = {'name':0,'gpsFile':1}

class mfv:
    
    __slots__ = ['name','gpsFile']
    def __init__(self, mfvNumber:str , gpsFile:str = ''):
        self.name = str(mfvNumber)
        self.gpsFile = str(gpsFile)



    def toItems(self) -> list[QStandardItem]:
        return [QStandardItem(self.name),QStandardItem(self.gpsFile)]
        
        



class mfvModel(QStandardItemModel):

    
    def __init__(self,parent:QWidget|None = None):
        super().__init__(0,len(COLS),parent)
        self.setHorizontalHeaderLabels(COLS.keys())



    def addMfv(self, data:mfv ):
        self.insertRow(0,data.toItems())
        

    def upload(self,db:QSqlDatabase):
        pass


    @staticmethod
    def fromDatabase(db:QSqlDatabase) -> 'mfvModel':
        m = mfvModel()
        q = runQuery(db=db,query = 'select mfv_ref,gps_file from mfv')
        while q.next():
            m.addMfv(mfv(str(q.value(0)),str(q.value(1))))
        return m
    





class customMfvModel:
    def __init__(self):
        self.mfvs = {}
        
        
    def rowCount(self, parent:QModelIndex = QModelIndex()) -> int:
        return len(self.mfvs)
        
    def columnCount(self, parent:QModelIndex = QModelIndex()) -> int:
        return 2
        
    
    def index(self,row:int,column:int,parent:QModelIndex = QModelIndex()):
        pass
        
    
def test():
    m = mfvModel()
    print(m.rowCount())
    d = mfv('test','')
    m.addMfv(d)
    d = mfv('test2','gps2')
    m.addMfv(d)
    print(m.rowCount())
    
    view = QTableView()
    view.setModel(m)
    view.show()
    return view


def testFromDatabase():
    db = defaultDb()
    m = mfvModel().fromDatabase(db)
    print(m.rowCount())

if __name__ == '__console__':
    #v = test()
    testFromDatabase()
        