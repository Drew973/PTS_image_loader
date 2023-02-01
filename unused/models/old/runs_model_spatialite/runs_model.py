# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 11:47:06 2022

mark in details and load:
    
    set 

@author: Drew.Bennett
"""
from PyQt5.QtSql import QSqlQuery ,QSqlDatabase,QSqlTableModel
from PyQt5.QtCore import Qt
from image_loader import exceptions


    #checks query text and returns QSqlQuery
def preparedQuery(text,db):
    query = QSqlQuery(db)
    if not query.prepare(text):
        print(text)
        raise exceptions.imageLoaderQueryError(query)
    return query

def runQuery(text,db,bindValues={}):
    q = preparedQuery(text,db)
    
    for k in bindValues:
        q.bindValue(k,bindValues[k])
    
    if not q.exec():
        raise exceptions.imageLoaderQueryError(q)
    return q


class runsModel(QSqlTableModel):
    
    def __init__(self,db=None,parent=None):
        if db is None:
            db = QSqlDatabase.database('image_loader')
        super().__init__(parent=parent,db=db)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setTable('runs')
        self.setFilter('1=1 order by round(run),run')
        self.select()
        
    
 
    
    '''
        update runs table then select
        using on conflict do update gives syntax errors for older versions of sqlite/qgis
    '''
    def select(self):
     #   print('runsModel.select')
        if self.database().isOpen():
            
            queries = []         
            
            queries.append('delete from runs where not run in (select run from details group by run)')
            
            queries.append('''
            INSERT INTO runs (run, min_id,max_id,start_id,end_id)
            select run,min(image_id) as min_id ,max(image_id) as max_id,min(image_id),max(image_id) 
            from details group by run
            ON CONFLICT (run) DO UPDATE SET min_id=excluded.min_id,max_id=excluded.max_id,
            start_id = max(start_id,excluded.min_id),end_id = min(end_id,excluded.max_id)
            ''')
          #insert and update min/max and start/end id
   
            for q in queries:
             #   print(q)
                runQuery(q,self.database())
            
            return super().select()
        else:
            return False



    def setData(self,index,value,role= Qt.EditRole):
        if index.column() == self.fieldIndex('load') and role == Qt.CheckStateRole:          
            if value == Qt.Checked:
                v = 1
            else:
                v = 0
            r = super().setData(index,v,Qt.EditRole)
          #  print('setData. value={v} sucessfull={r}'.format(r=r,v=v))
            return r
        return super().setData(index,value,role)
    
    
    
    #converting run to float bad idea because eg float(100_6) = 1006.0.
    def data(self,index,role=Qt.EditRole):
        #SQlite has dynamic types.
        
        if index.column() == self.fieldIndex('load'):
            
            if role == Qt.DisplayRole:
                return ''
                
            if role == Qt.EditRole:
                return bool(super().data(index,role))    
            
            if  role == Qt.CheckStateRole:
                if super().data(index,Qt.EditRole) ==1:
                    return Qt.Checked
                else:
                    return Qt.Unchecked
        
       # if role == Qt.DisplayRole and index.column() == self.fieldIndex('start_id'):
        #    return int(str(super().data(index,role)))
 
       # if role == Qt.DisplayRole and index.column() == self.fieldIndex('end_id'):
       #     return int(str(super().data(index,Qt.DisplayRole).value()))
    
        return super().data(index,role)
        
        
        
    def flags(self,index):
        if index.column()==self.fieldIndex('load'):
            return super().flags(index) | Qt.ItemIsUserCheckable
        
        if index.column()==self.fieldIndex('start_id'):
            return super().flags(index)
        
        if index.column()==self.fieldIndex('end_id'):
            return super().flags(index)  
        
        return super().flags(index)& ~Qt.ItemIsEditable



    def maxValue(self,index):
        if index.column() == self.fieldIndex('start_id') or index.column() == self.fieldIndex('end_id'):
            return index.sibling(index.row(),self.fieldIndex('max_id')).data()
        else:
            raise NotImplementedError
            
       
    def minValue(self,index):
         if index.column() == self.fieldIndex('start_id') or index.column() == self.fieldIndex('end_id'):
            return index.sibling(index.row(),self.fieldIndex('min_id')).data()
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
              