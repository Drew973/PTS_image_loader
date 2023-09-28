# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 09:42:07 2023

@author: Drew.Bennett
"""


from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase
from image_loader import db_functions
from qgis.core import QgsPointXY


class correctionsModel(QSqlQueryModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
       # self._db = db
        #db_functions.createDb()
        self.setRun('')


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
        db_functions.runQuery(query = 'delete from corrections where pk in (:pks)'
                              , db = self.database()
                              ,values={':pks':','.join(pks)})
        self.select()
        
        
    def select(self):
        self.setQuery(self.query().lastQuery(),self.database())
       #self.setQuery(self.query()) query does not update model. bug in qt?


    def setRunForItems(self,indexes,run):
       col = self.fieldIndex('pk')
       pks = [str(self.index(index.row(),col).data()) for index in indexes]
       q = "update corrections set run = ':run' where pk in ({pks})".format(pks = ','.join(pks))
       db_functions.runQuery(query = q,values={':run':run})
       self.select()               
               
               
    def setRun(self,run):
        self._run = run
        if run:
            filt = "where run = '{run}'".format(run=run)#"
        else:
            filt = ''
            #original
        #filt = ''
        q = 'select run,pk,frame_id,pixel,line,new_x,new_y from corrections {filt} order by frame_id,line'.format(filt=filt)
        self.setQuery(q,self.database())

    
    #insert or update correction. pk = None for insert.
  
    def setCorrection(self,pk,run,frameId,pixel,line,newX,newY):
       # print('setCorrection',pk,run,frameId,pixel,line,newX,newY)
        if pk is None:
            db_functions.runQuery(query = 'insert into corrections (run,frame_id,pixel,line,new_x,new_y) values (:run,:frame,:pixel,:line,:new_x,:new_y)',
                                  values = {':run':run,':frame':frameId,':new_x':newX,':new_y':newY,':pixel':pixel,':line':line})
        else:
            db_functions.runQuery(query = 'update corrections SET run = :run,frame_id=:frame,new_x = :new_x,new_y = :new_y,pixel = :pixel ,line = :line where pk = :pk',
                                  values = {':run':run,':frame':frameId,':new_x':newX,':new_y':newY,':pixel':pixel,':line':line,':pk':pk})
        self.select()
        
        
        
    def hasGps(self):
        return db_functions.hasGps()
        
    
    def loadFile(self,file):
        db_functions.loadCorrections(file)
        self.select()
        

#chainage:float,offset:float,index:QModelIndex -> QgsPointXY
    def getPoint(self,frameId,pixel,line):
        return db_functions.getPoint(frameId,pixel,line)
        
        


    #from last image position    
    def getPixelLine(self,frameId,point):
        'select '
        pass