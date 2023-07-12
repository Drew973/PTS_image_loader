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
        
        if run:
            filt = "where run = '{run}'".format(run=run)#"
        else:
            filt = ''
            #original
        #filt = ''
        q = 'select pk,chainage,original_x,original_y,new_x,new_y from corrections {filt} order by chainage'.format(filt=filt)
        self.setQuery(q,self.database())


        
    def addCorrections(self,corrections):
        q = QSqlQuery(self.database())
        if q.prepare('insert into corrections(run,chainage,original_x,original_y,new_x,new_y) values (:run,:chainage,:original_x,:original_y,:new_x,:new_y)'):
            for r in corrections:
                q.bindValue(':run',r['run'])
                q.bindValue(':chainage',r['chainage'])
                q.bindValue(':new_x',r['new_x'])
                q.bindValue(':new_y',r['new_y'])
                q.bindValue(':original_x',r['original_x'])
                q.bindValue(':original_y',r['original_y'])
    
                if not q.exec():
                    print(q.boundValues())
                    raise db_functions.queryError(q)
        else:
            raise db_functions.queryPrepareError(q)
        self.select()
        
    
    def editCorrection(self,index,chainage,startX,startY,endX,endY):
        if not index.isValid():
            self.addCorrections([{'run':self._run,'chainage':chainage,'original_x':startX,'original_y':startY,'new_x':endX,'new_y':endY}])
            return
        pk = self.index(index.row(),self.fieldIndex('pk')).data()
      #  print(pk)
        updateQuery = "update corrections set run = ':run',chainage=:ch,original_x = :sx,original_y = :sy,new_x=:ex,new_y=:ey where pk = :pk"
        db_functions.runQuery(query = updateQuery,values = {':run':self._run,':ch':chainage,':sx':startX,':sy':startY,':ex':endX,':ey':endY,':pk':pk})
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
    find closest chainage
    index unused
    '''
    #index QModelIndex,point:QgsPointXY -> (chainage float,offset float)
    def getChainage(self,point,index=None):
       # print('run:',self.run)
        return db_functions.getChainage(run = self._run,
                                        x = point.x(),
                                        y = point.y(),
                                        db = self.database())
    