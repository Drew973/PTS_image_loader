# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 09:42:07 2023

@author: Drew.Bennett
"""


from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase
from image_loader import db_functions


class correctionsModel(QSqlQueryModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setRange(0,0)


    def fieldIndex(self,name):
        return self.record().indexOf(name)


    def database(self):
        return QSqlDatabase.database('image_loader')


    def clear(self):
        q = QSqlQuery(self.database())
        if not q.exec('delete from corrections'):
            raise db_functions.queryError(q)
        self.select()

    
    def allowedRange(self,index):
        return (0,999999)
        
        
    def dropRows(self,indexes):
        col = self.fieldIndex('pk')
        pks = [str(self.index(index.row(),col).data()) for index in indexes]
        #print('drop pks',pks)
        db_functions.runQuery(query = 'delete from corrections where pk in (:pks)'
                              , db = self.database()
                              ,values = {':pks':','.join(pks)})
        self.select()
        
        
    def select(self):
        #self.setQuery(self.query().lastQuery(),self.database())
       #self.setQuery(self.query()) query does not update model. bug in qt?
       self.query().exec()
       self.setQuery(self.query())


    def setRange(self,startFrame,endFrame):
       # s = startChainage/HEIGHT
       # e = endChainage/HEIGHT
        qs = 'select pk,frame_id,pixel,line,new_x,new_y from corrections where frame_id >= :s and frame_id<:e order by frame_id,line'
        q = QSqlQuery(self.database())
        q.prepare(qs)
        q.bindValue(':s',startFrame)
        q.bindValue(':e',endFrame)
        q.exec()
        self.setQuery(q)

    
    #insert or update correction. pk = None for insert.
    def setCorrection(self,pk,frameId,pixel,line,newX,newY):
       # print('setCorrection',pk,run,frameId,pixel,line,newX,newY)
        if pk is None:
            db_functions.runQuery(query = 'insert into corrections (frame_id,pixel,line,new_x,new_y) values (:frame,:pixel,:line,:new_x,:new_y)',
                                  values = {':frame':frameId,':new_x':newX,':new_y':newY,':pixel':pixel,':line':line})
        else:
            db_functions.runQuery(query = 'update corrections SET frame_id=:frame,new_x = :new_x,new_y = :new_y,pixel = :pixel ,line = :line where pk = :pk',
                                  values = {':frame':frameId,':new_x':newX,':new_y':newY,':pixel':pixel,':line':line,':pk':pk})
        self.select()

        
    def hasGps(self):
        return db_functions.hasGps()
        
    
    def loadFile(self,file):
        db_functions.loadCorrections(file)
        self.select()
        
