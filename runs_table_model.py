# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:12:37 2023

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlQueryModel,QSqlQuery
from PyQt5.QtCore import Qt
from image_loader.db_functions import runQuery,defaultDb
import numpy as np


class runsTableModel(QSqlQueryModel):
    
    def __init__(self,db=None,parent=None):
        super().__init__(parent)
        self.select()
      
        
    def database(self):
        return defaultDb()
    
    
    def fieldIndex(self,field):
        return self.record().indexOf(field)
    
    
    def fieldName(self,field):
       return self.record().fieldName(field)
    
    
    def flags(self,index):
        if index.column() == self.fieldIndex('number'):
            return Qt.ItemIsSelectable|Qt.ItemIsEnabled
        return Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable
        
    
    def clear(self):
        runQuery('delete from runs')
        self.select()
        
    
    #[{start_frame,end_frame}]
    def addRuns(self,runs):
        db = self.database()
        db.transaction()
        for r in runs:
            runQuery(query = 'insert OR IGNORE into runs(start_frame,end_frame) values (:s,:e)',db=db,values = {':s':r['start_frame'],':e':r['end_frame']})    
        db.commit()
        self.select()
        
        
    def select(self):
        #q = 'select ROW_NUMBER() over (order by start_frame,end_frame) as number,pk ,start_frame,end_frame,chainage_correction,left_offset from runs order by start_frame,end_frame'
        q = 'select number,pk ,start_frame,end_frame from runs_view order by start_frame,end_frame'       
        self.setQuery(q,self.database())
        
     
  #  #def data(self,index,role=Qt.DisplayRole):
      #  if role in (Qt.EditRole,Qt.DisplayRole) and index.column() == self.fieldIndex('number'):
       #     d = super().data(index,role)
       #     return int(d)
     #   return super().data(index,role)        
        
    
    def setData(self,index,value,role=Qt.EditRole):
        if role == Qt.EditRole and value != index.data():
            pk = self.index(index.row(),self.fieldIndex('pk')).data()
            q = 'update runs set {col} = :val where pk = :pk'.format(col = self.fieldName(index.column()))
          #  print(q,'val',value,'pk',pk)
            runQuery(query = q,values = {':pk':pk,':val':value})
            self.select()
            return super().setData(index,value,role)
        return super().setData(index,value,role)
    
    
    def dropRuns(self,pks):
   #     print('pks',pks)
        pks = [str(pk) for pk in pks]
        q = 'delete from runs where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        runQuery(q)
        self.select()
        