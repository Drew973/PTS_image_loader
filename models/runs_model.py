# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:25:12 2022

@author: Drew.Bennett


model containing info about which images to load.


from database:
    run
    start
    end

display


"""
import logging
logger = logging.getLogger(__name__)

#import sqlite3
from PyQt5.QtSql import QSqlQueryModel, QSqlQuery ,QSqlDatabase
from PyQt5.QtCore import Qt



class runsModel(QSqlQueryModel ):
    
    def __init__(self,parent=None):
        logger.debug('__init__')
        super().__init__(parent=parent)
        self.select()
        self.data = {}
        
       
        
    def select(self):
        #round() returns float made of any digits in text,0 if none
        self.setQuery(QSqlQuery('select run,max(image_id),min(image_id) from details group by run order by round(run),run',QSqlDatabase.database('image_loader')))


    def fieldIndex(self,name):
        return self.record().indexOf(name)
       
        
       
        
    #converting run to float bad idea because eg float(100_6) = 1006.0.
    def data(self,index,role=Qt.DisplayRole):
        #SQlite has weird/no types.
        if (role == Qt.DisplayRole or role == Qt.EditRole) and index.column() == self.fieldIndex('show'):
            return bool(super().data(index,role))    
        
        if  role == Qt.CheckStateRole and index.column() == self.fieldIndex('show'):
            if bool(super().data(index,Qt.DisplayRole)):
                return Qt.Checked
            else:
                return Qt.Unchecked
        
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('start_id'):
            return int(super().data(index,role))
 
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('end_id'):
            return int(super().data(index,Qt.DisplayRole))
    
        return super().data(index,role)
        
        
        
    def flags(self,index):
        if index.column()==self.fieldIndex('show'):
          #  return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
            return super().flags(index) | Qt.ItemIsUserCheckable
        
        #prevent editing run column.
        if index.column()==self.fieldIndex('run'):
            return super().flags(index) & ~Qt.ItemIsEditable
        
        return super().flags(index)



    def maxValue(self,index):
        if index.column() == self.fieldIndex('start_id') or index.column() == self.fieldIndex('end_id'):
            return index.sibling(index.row(),self.fieldIndex('max')).data()
        else:
            raise NotImplementedError
            
       
    def minValue(self,index):
         if index.column() == self.fieldIndex('start_id') or index.column() == self.fieldIndex('end_id'):
            return index.sibling(index.row(),self.fieldIndex('min')).data()
         else:
            raise NotImplementedError  


    def framesLayer(self):
        if self.parent() is not None:
            return self.parent().framesLayer()
    

    def idField(self):
        if self.parent() is not None:
            return self.parent().idField()
        
        
    def runField(self):
        if self.parent() is not None:
            return self.parent().runField()
    
    

    def idFromFeatures(self,index):
        layer = self.framesLayer()
        field = self.idField()
        runField = self.runField()
        run = index.sibling(index.row(),self.fieldIndex('run')).data()
        if layer is not None and field is not None and runField is not None:
            ids = [int(f[field]) for f in layer.selectedFeatures() if f[runField]==run]
            if ids:
                if index.column()==self.fieldIndex('start_id'):
                    return min(ids)
                if index.column()==self.fieldIndex('end_id'):
                    return max(ids)                 


    def setFromFeatures(self,index):
        i = self.idFromFeatures(index)
        if i is not None:
            self.setData(index,i)
              