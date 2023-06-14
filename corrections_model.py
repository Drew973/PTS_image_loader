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
        
        
        

    def select(self):
        self.setQuery(self.query().lastQuery(),self.database())
       #self.setQuery(self.query()) query does not update model. bug in qt?



    def setRun(self,run):
        self._run = run
        
 #       if run:
   #         filt = "where run = '{run}'".format(run=run)#"
   #     else:
    #        filt = ''
            #original
        filt = ''
        q = 'select pk,original_chainage,original_offset,new_chainage,new_offset from corrections {filt} order by original_chainage'.format(filt=filt)
        self.setQuery(q,self.database())


        
    def addCorrections(self,corrections):
        db_functions.insertCorrections(corrections=corrections,db = self.database())
        self.select()
        
    
        
    def loadFile(self,file):
        db_functions.loadCorrections(file)
        self.select()
        


#chainage:float,offset:float,index:QModelIndex -> QgsPointXY
    def getPoint(self,chainage,offset,index=None):
        return db_functions.getPoint(chainage=chainage,offset=offset,db=self.database())
      
    
    
    '''
    find closest chainage & offset of closest point within run
    '''
    #index QModelIndex,point:QgsPointXY -> (chainage float,offset float)
    def getChainage(self,point,index):
        
        run = self.index(index.row(),self.fieldIndex('run')).data()
        if run is None:
            run = ''
            
        return db_functions.getChainage(run = run,
                                        x = point.x(),
                                        y = point.y(),
                                        db = self.database())
    