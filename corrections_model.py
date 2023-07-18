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
        q = 'select run,pk,chainage,new_x,new_y,current_x,current_y from corrections_view {filt} order by chainage'.format(filt=filt)
        self.setQuery(q,self.database())


        
#    def addCorrections(self,corrections):
#        q = QSqlQuery(self.database())
#        if q.prepare('insert into corrections(run,chainage,x,y) values (:run,:chainage,:x,:y)'):
#            for r in corrections:
#                q.bindValue(':run',r['run'])
#                q.bindValue(':chainage',r['chainage'])
 #               q.bindValue(':x',r['x'])
 #               q.bindValue(':y',r['y'])
#                if not q.exec():
 #                   print(q.boundValues())
#                    raise db_functions.queryError(q)
   #     else:
 #          raise db_functions.queryPrepareError(q)
  #     self.select()
        
    
    
    #x_offset is x difference between point & corrected chainage.
    def setCorrection(self,chainage,currentPosition,newPosition):
        #select Line_Interpolate_Point(corrected_line,(:ch-m)/(next_m-m)) from lines_view where m <= :ch and :ch <=next_m
        
       # pt = db_functions.getPoint(chainage=chainage,db=self.database())
        
        correctedPt = db_functions.getCorrectedPoint(chainage=chainage,db=self.database())
        xo = currentPosition[0]-correctedPt.x()#x offset from chainage to currentPosition
        yo = currentPosition[1]-correctedPt.y()#y offset from chainage to currentPosition
      #  print('xo',xo,'yo',yo)
        updateQuery = """
        insert into corrections (run,chainage,new_x,new_y,x_offset,y_offset) values (':run',:ch,:new_x,:new_y,:xo,:yo)
        ON CONFLICT DO UPDATE SET run = ':run',chainage=:ch,new_x = :new_x,new_y = :new_y,x_offset = :xo,y_offset=:yo
        """
        db_functions.runQuery(query = updateQuery,values = {':run':self._run,':ch':chainage,':new_x':newPosition[0],':new_y':newPosition[1],':xo':xo,':yo':yo})
        self.select()
        
        
    def hasGps(self):
        return db_functions.hasGps()
        
    
    def loadFile(self,file):
        db_functions.loadCorrections(file)
        self.select()
        

#chainage:float,offset:float,index:QModelIndex -> QgsPointXY
    def getPoint(self,chainage,index=None):
        return db_functions.getPoint(chainage=chainage,db=self.database())
      
    
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
    