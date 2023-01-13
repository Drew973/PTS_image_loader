# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 11:47:06 2022

mark in details and load:
    
    set 

@author: Drew.Bennett
"""
from PyQt5.QtSql import QSqlQuery ,QSqlDatabase,QSqlTableModel
from PyQt5.QtCore import Qt



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
        
        if self.database().isOpen():
            e = self.database().exec('delete from runs where not run in (select run from details group by run)').lastError()
            if e.isValid():
                raise ValueError(e.text())
                
            queries = []
            queries.append('drop table if exists t')
            queries.append('create table t as select run as r,start_id as s,end_id as e from runs')
            queries.append('delete from runs')
            
            q = '''
            insert into runs (run,load,min_id,max_id,start_id,end_id) select 
            run,False,mini,maxi
            ,case when mini<=t.s and t.s<=maxi then t.s else mini end
            ,case when mini<=t.e and t.e<=maxi then t.e else maxi end
            from
            (select run,min(image_id) as mini,max(image_id) as maxi 
            from details group by run) a
            left join t on r=run
            '''
            queries.append(q)
            queries.append('drop table if exists t')
    
            for q in queries:
                e = self.database().exec(q).lastError()
                if e.isValid():
                    raise ValueError(e.text())
            return super().select()
        else:
            return False

    #converting run to float bad idea because eg float(100_6) = 1006.0.
    def data(self,index,role=Qt.EditRole):
        #SQlite has dynamic types.
        
        if index.column() == self.fieldIndex('load'):
            
            if role == Qt.DisplayRole:
                return ''
                
            if role == Qt.EditRole:
                return bool(super().data(index,role))    
            
            if  role == Qt.CheckStateRole:
                if bool(self.data(index,Qt.EditRole)):
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
    
    
    def markInDetails(self):
        self.database().exec('update details set load = runs.load and start_id<=image_id and image_id<=end_id from runs where runs.run=details.run')
    

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
              