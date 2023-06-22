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
        
    
    def editCorrection(self,index,originalChainage,newChainage,originalOffset,newOffset):
        if not index.isValid():
            self.addCorrections([{'run':self._run,'original_chainage':originalChainage,'original_offset':originalOffset,'new_chainage':newChainage,'new_offset':newOffset}])
            return
        
        pk = self.index(index.row(),self.fieldIndex('pk')).data()
      #  print(pk)
        updateQuery = 'update corrections set original_chainage = {sch} , new_chainage = {ech},original_offset = {soff} , new_offset = {noff} where pk = {pk}'
        t = updateQuery.format(sch = originalChainage ,ech = newChainage,soff = originalOffset,noff = newOffset,pk=pk)
        db_functions.runQuery(db = self.database(),query = t)
        self.select()
        
        
    def hasGps(self):
        return db_functions.hasGps()
        
    def loadFile(self,file):
        db_functions.loadCorrections(file)
        self.select()
        


#chainage:float,offset:float,index:QModelIndex -> QgsPointXY
    def getPoint(self,chainage,offset,index=None):
        return db_functions.getPoint(chainage=chainage,offset=offset,db=self.database())
      
    
    
    '''
    find closest chainage & offset of closest point within run
    index unused
    '''
    #index QModelIndex,point:QgsPointXY -> (chainage float,offset float)
    def getChainage(self,point,index=None):
       # print('run:',self.run)
        return db_functions.getChainage(run = self._run,
                                        x = point.x(),
                                        y = point.y(),
                                        db = self.database())
    