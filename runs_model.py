# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:12:37 2023

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtCore import Qt
import numpy as np
from image_loader.dims import mToFrame
from image_loader.db_functions import runQuery,defaultDb,prepareQuery,queryError



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
        q = 'select number,pk ,start_frame,end_frame,chainage_shift,offset,correction_start_m,correction_end_m,correction_start_offset,correction_end_offset from runs_view order by start_frame,end_frame'       
        self.setQuery(q,self.database())
        
     
  #  #def data(self,index,role=Qt.DisplayRole):
      #  if role in (Qt.EditRole,Qt.DisplayRole) and index.column() == self.fieldIndex('number'):
       #     d = super().data(index,role)
       #     return int(d)
     #   return super().data(index,role)        
        
    
    def setData(self,index,value,role=Qt.EditRole):
        if role == Qt.EditRole and value != index.data():
        #    print('setData',index.row(),index.column(),value)
             
            pk = self.index(index.row(),self.fieldIndex('pk')).data()
            q = 'update runs set {col} = :val where pk = :pk'.format(col = self.fieldName(index.column()))

            if index.column() == self.fieldIndex('chainage_shift'):
                q = 'update runs set correction_start_m = 0.0, correction_end_m = :val where pk = :pk'
           
            if index.column() == self.fieldIndex('offset'):
                q = 'update runs set correction_start_offset = 0.0, correction_end_offset = :val where pk = :pk'
                
          #  print(q,'val',value,'pk',pk)
            runQuery(query = q,values = {':pk':pk,':val':value})
            self.select()
            return True
        return super().setData(index,value,role)
    
    
    def setCorrection(self,pk,startM,endM,startOffset,endOffset):
        qs = 'update runs set correction_start_m = :s , correction_end_m = :e , correction_start_offset = :so, correction_end_offset = :eo where pk = :pk'
        runQuery(query = qs,values = {':pk':pk,':s':startM,':e':endM,':so':startOffset,':eo':endOffset})
        self.select()

    
    def dropRuns(self,pks):
   #     print('pks',pks)
        pks = [str(pk) for pk in pks]
        q = 'delete from runs where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        runQuery(q)
        self.select()
        
        
    #array -> array
    @staticmethod
    def correctMO(mo):
        q = prepareQuery('select m_shift,offset from runs_view where start_frame < :f and end_frame >= :f order by start_frame limit 1')
        r = np.empty((len(mo),2),dtype = float)
        r = np.nan
        for i,row in enumerate(mo):
            q.bindValue(':f',int(mToFrame(row[0])))
            if not q.exec():
                raise queryError(q)
            while q.next():
                r[i,0] = mo[i,0] + q.value(0)
                r[i,1] = mo[i,1] + q.value(1)
        return r