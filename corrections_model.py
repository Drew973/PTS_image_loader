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
        db_functions.createDb()
        self.setRun('')



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
        
        if run:
            filt = "where run = '{run}'".format(run=run)#"
        else:
            filt = ''
        q = 'select pk,start_chainage,start_offset,end_chainage,end_offset from corrections {filt} order by start_chainage'.format(filt=filt)
        self.setQuery(q,self.database())



    #set chainage/offset corrections from startPoint and endPoint
    
   # QgsPointXY,QgsPointXY,QModelIndex
    def addCorrection(self,run,startChainage,endChainage,startOffset,endOffset):
        db_functions.runQuery(query = 'insert into corrections(run,start_chainage,end_chainage,start_offset,end_offset) values(:run,:startChainage,:endChainage,:startOffset,:endOffset)',
                             values = {':run':run,':startChainage':startChainage,':endChainage':endChainage,':startOffset':startOffset,':endOffset':endOffset} )
        self.select()
        
        
        
        
       # q = db_functions.runQuery("select start_chainage,end_chainage,end_offset-start_offset from corrections where run = '':run")
        
        