# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 08:41:07 2022

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlQuery
from image_loader import exceptions


    #checks query text and returns QSqlQuery
def preparedQuery(text,db):
    query = QSqlQuery(db)
    if not query.prepare(text):
        print(text)
        raise exceptions.imageLoaderQueryError(query)
    return query



#attempts to run query .Raise imageLoaderQueryError on failure.

#"For SQLite, the query string can contain only one statement at a time. If more than one statements are give, the function returns false"
#Wrong. Query doesn't execute but exec() is returning True
def runQuery(text,db,bindValues={}):
    q = preparedQuery(text,db)
    
    for k in bindValues:
        q.bindValue(k,bindValues[k])
    
    if not q.exec():
        raise exceptions.imageLoaderQueryError(q)
    return q
    



'''
       for spatiallite add
      #  "SELECT load_extension('mod_spatialite')",
 #"SELECT InitSpatialMetadata(1)",
     #  runQuery("SELECT load_extension('mod_spatialite')",db)
    #   runQuery("SELECT InitSpatialMetadata(1)",db)

 #      runQuery("SELECT AddGeometryColumn('image_details', 'geom', 27700, 'POLYGON')",db)
'''

def createDetailsTable(db):
       q = '''
            CREATE TABLE if not exists details (
                pk integer primary key,
                run varchar NOT NULL,
                image_id int NOT NULL,
                file_path VARCHAR NOT NULL,
                name varchar,
                groups varchar
            )
            '''
       runQuery(q,db)
       

       
#sqlite doesn't realy have bool. it uses integer instead.
def createRunsTable(db):
    q = '''
            CREATE TABLE runs (
                run varchar NOT NULL primary key,
                show bool default False,
                start_id int NOT NULL,
                end_id int NOT NULL          
            )
        '''        
    runQuery(q,db)    

    

 
def setupDb(db):
    runQuery('drop table if exists details',db)
    runQuery('drop table if exists runs',db)
    createDetailsTable(db)
    createRunsTable(db)
    #createRunsTriggers(db)
       
    
from image_loader.test.get_db import getDb

def test(db=getDb()):
    setupDb(db)
    
if __name__ == '__console__' or __name__ == '__main__':
    test()
    
    