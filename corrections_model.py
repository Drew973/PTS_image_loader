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
        q = 'select run,pk,chainage,new_x,new_y,current_x,current_y,x_offset,y_offset from corrections_view {filt} order by chainage'.format(filt=filt)
        self.setQuery(q,self.database())

    
    #insert or update correction. pk = None for insert.
    #x_offset is x difference between point & corrected chainage.
    def setCorrection(self,pk,chainage,xOffset,yOffset,newX,newY):
        
   #     print('setCorrection. pk = ',pk)
        if pk is None:
            db_functions.runQuery(query = 'insert into corrections (run,chainage,new_x,new_y,x_offset,y_offset) values (:run,:ch,:new_x,:new_y,:xo,:yo)',
                                  values = {':run':self._run,':ch':chainage,':new_x':newX,':new_y':newY,':xo':xOffset,':yo':yOffset})
        else:
            db_functions.runQuery(query = 'update corrections SET run = :run,chainage=:ch,new_x = :new_x,new_y = :new_y,x_offset = :xo,y_offset=:yo where pk = :pk',
                                  values = {':run':self._run,':ch':chainage,':new_x':newX,':new_y':newY,':xo':xOffset,':yo':yOffset,':pk':pk})
        self.select()
        
        
        
    def hasGps(self):
        return db_functions.hasGps()
        
    
    def loadFile(self,file):
        db_functions.loadCorrections(file)
        self.select()
        

#chainage:float,offset:float,index:QModelIndex -> QgsPointXY
    def getPoint(self,chainage,xOffset,yOffset,index=None):
        pt = db_functions.getCorrectedPoint(chainage=chainage,db=self.database())
        return QgsPointXY(pt.x()+xOffset,pt.y()+yOffset)
    
    '''
    find closest (chainage,x_offset,y_offset)
    index unused
    '''
    #index QModelIndex,point:QgsPointXY -> (chainage float,xOffset float,yOffset float)
    def getChainage(self,point,index=None):
       # print('run:',self.run)
        ch = db_functions.getCorrectedChainage(run = self._run,
                                        x = point.x(),
                                        y = point.y(),
                                        db = self.database())
        
        pt = db_functions.getCorrectedPoint(chainage =ch,db = self.database())#snapped to corrected line.
        
        return (ch , point.x()-pt.x() , point.y()-pt.y() )
        
        
    