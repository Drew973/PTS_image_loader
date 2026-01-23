# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 15:42:30 2026

@author: Drew.Bennett
"""

from PyQt5.QtCore import QModelIndex,Qt


from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTableView
from PyQt5.QtSql import QSqlDatabase

from image_loader.db_functions import runQuery,defaultDb
from PyQt5.QtCore import QAbstractItemModel


from enum import Enum




#COLS = {'name':0,'gpsFile':1}

class COLS(Enum):
    name = 0
    gpsFile = 1


class mfv:
    
    __slots__ = ['name','gpsFile']
    def __init__(self, mfvNumber:str , gpsFile:str = ''):
        self.name = str(mfvNumber)
        self.gpsFile = str(gpsFile)



    def toItems(self) -> list[QStandardItem]:
        return [QStandardItem(self.name),QStandardItem(self.gpsFile)]
        
        





class mfvModel(QAbstractItemModel):
    def __init__(self,parent:QWidget|None = None):
        self.mfvs = []
        super().__init__(parent)
        
        
        
    def rowCount(self, parent:QModelIndex = QModelIndex()) -> int:
        return len(self.mfvs)
        
    def columnCount(self, parent:QModelIndex = QModelIndex()) -> int:
        return 2
        
    
    def index(self,row:int,column:int,parent:QModelIndex = QModelIndex()) -> QModelIndex:
        i = QModelIndex()
    #    i.setData(self.mfvs[row].name)
        return i
        
    
    
    def data(self,index,role = Qt.DisplayRole):
        if role in (Qt.DisplayRole,Qt.EditRole):
            if index.column() == COLS.name:
                return self.mfvs[index.row()].name

            if index.column() == COLS.gpsFile:
                return self.mfvs[index.row()].name
            
            
            
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return COLS(section).name
        
    
    def addMfv(self,data:mfv):
        self.mfvs.append(mfv)
    
    
    
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


#def testFromDatabase():
    #db = defaultDb()
   # m = mfvModel().fromDatabase(db)
   # print(m.rowCount())

if __name__ == '__console__':
    v = test()
   # testFromDatabase()
        