# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:25:12 2022

@author: Drew.Bennett

items have:
filePath: absolute path. doesn't need to be unique. when loading csv allow directory with csv + relative path
groups: list of groups. loaded to image_loader.groups[0].groups[1]...
run
image_id

combination of run and image_id should be unique

"""

#import sqlite3
from PyQt5.QtSql import QSqlQuery,QSqlTableModel
from PyQt5.QtCore import Qt



class runsModel(QSqlTableModel):
    
    
    def __init__(self,db,parent=None):
        
        super().__init__(parent=parent,db=db)
        
        self.setTable('runs')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()
       
    
    
    def data(self,index,role):
        #SQlite has weird type checking.
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('show'):
            return bool(super().data(index,role))    
        
        
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('start_id'):
            return int(super().data(index,role))
 
        
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('end_id'):
            return int(super().data(index,role))
        
    
        return super().data(index,role)

    
    
    def updateTable(self):
      #  print('runsModel.updateTable()')
        #INSERT OR IGNORE when updating runs info.
        
        q = '''insert or ignore into runs(run,start_id,end_id)
        select run,min(image_id),max(image_id) from image_details 
        group by run;
        '''
        
        runQuery(q,self.database())
        
        q = 'delete from runs where not run in (select distinct run from image_details);'
        runQuery(q,self.database())
        self.select()



    def selectAll(self):
        q = 'update runs set show=True;'
        runQuery(q,self.database())
        self.select()



    def clearTable(self):
        runQuery('delete from runs',self.database())
        self.select()



class imageLoaderError(Exception):
    pass



class imageLoaderQueryError(Exception):
    def __init__(self,q):
        message = 'query "%s" failed with "%s"'%(q.lastQuery(),q.lastError().databaseText())
        super().__init__(message)

        

#attempts to run query .Raise imageLoaderQueryError on failure.
def runQuery(text,db):
    q = preparedQuery(text,db)
    if not q.exec():
        raise imageLoaderQueryError(q)
    

    
    #checks query text and returns QSqlQuery
def preparedQuery(text,db):
    query = QSqlQuery(db)
    if not query.prepare(text):
        raise imageLoaderQueryError(query)
    return query
    


#sqlite doesn't realy have bool. it uses integer instead.
def createTable(db):
    q = '''
            CREATE TABLE runs (
                run varchar NOT NULL primary key,
                show bool default False,
                start_id int NOT NULL,
                end_id int NOT NULL          
            )
        '''        
    runQuery(q,db)    
    
    
    
#unused
def createTriggers(db):
    #create triggers
    q = '''
    CREATE TRIGGER IF NOT EXISTS details_insert 
   AFTER INSERT
   ON image_details
   BEGIN
       insert or ignore into runs(run,start_id,end_id)
       select run,min(image_id),max(image_id) from image_details 
       where run =NEW.run;
    END;
    '''
    runQuery(q,db)
    
    
    q = '''
    CREATE TRIGGER IF NOT EXISTS details_delete
    AFTER delete
    ON image_details
    BEGIN
       delete from runs where not run in (select distinct run from image_details);
    END;
    '''
    runQuery(q,db)
    
    
    q = '''
    CREATE TRIGGER IF NOT EXISTS details_update
    AFTER update
    ON image_details
    BEGIN
       delete from runs where not run in (select distinct run from image_details);

       insert or ignore into runs(run,start_id,end_id)
       select run,min(image_id),max(image_id) from image_details 
       group by run;
    END;
    '''
    runQuery(q,db)  