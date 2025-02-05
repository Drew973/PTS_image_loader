# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:12:37 2023

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtCore import Qt
import numpy as np
import csv
import io
from qgis.core import QgsGeometry
import typing
from image_loader.db_functions import runQuery,defaultDb
from image_loader.type_conversions import asFloat
from image_loader import settings , db_functions , dims
from qgis.core import QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsProject

from image_loader.backend import runs_functions


    
    
    
class runsModel(QSqlQueryModel):
    
    def __init__(self,db=None,parent=None):
        super().__init__(parent)
        self.select()
        self.gpsModel = None
        
      
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
    def addRuns(self,runs:typing.Iterable[int]):
        runs_functions.insertRuns(runs)
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
        
    #correction_start_m and correction_start_offset = 0 if editing table. otherwise where user clicked.
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
    
    
    def paste(self,text):
        runs_functions.loadText(text)
        self.select()
    
    
    def setCorrection(self , pk:int , startM:float , endM:float , startOffset:float , endOffset:float):
        qs = '''update runs set correction_start_m = :s - correction_end_m +correction_start_m , 
        correction_start_offset = :so - correction_end_offset + correction_start_offset, 
        correction_end_m = :e , correction_end_offset = :eo where pk = :pk'''
        runQuery(query = qs,values = {':pk':pk,':s':startM,':e':endM,':so':startOffset,':eo':endOffset})
        self.select()


    #pks:[int]
    def dropRuns(self,pks):
   #     print('pks',pks)
        pks = [str(pk) for pk in pks]
        q = 'delete from runs where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        runQuery(q)
        self.select()

        
    # array of [[m,o]] ordered by distance
    #run should only pass near point once...
    def locate(self , row : int, x : float , y : float) -> np.array:
        outsideRunDistance = asFloat(settings.value('outsideRunDistance') , 50.0)
        minM = dims.frameToM(int(self.index(row , self.fieldIndex('start_frame')).data())) - outsideRunDistance
        maxM = dims.frameToM(int(self.index(row , self.fieldIndex('end_frame')).data())) + outsideRunDistance
        return self.gpsModel.locate(x = x , y = y , minM = minM , maxM = maxM )#nearest within range.



