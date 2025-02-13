# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 14:28:37 2023

@author: Drew.Bennett

geopackage for easier debugging?
filelocks?


sqlite versions;
qgis 3.18 = sqlite 3.29.0


CTE added 3.8.3 ,

update from added in 3.33
upsert added in 3.24.0

"Generated column support was added with SQLite version 3.31.0 (2020-01-22). If an earlier version of SQLite attempts to
read a database file that contains a generated column in its schema, then that earlier version will perceive the generated 
column syntax as an error and will report that the database schema is corrupt"
    
"""
from PyQt5.QtSql import QSqlDatabase,QSqlQuery
from image_loader.file_locations import dbFile


class queryError(Exception):
    def __init__(self , query):
        super().__init__('error executing query {q}:{err}'.format(q = query.lastQuery(),err = query.lastError().text()))


class queryPrepareError(Exception):
    def __init__(self , query):
        super().__init__('error preparing query {q}:{err}'.format(q = query.lastQuery(),err = query.lastError().text()))
        
        
        
def defaultDb():
    return QSqlDatabase.database('image_loader')        
        

#from PyQt5.QtSql import QSqlDriver
   #print('has named placeholders',db.driver().hasFeature(QSqlDriver.NamedPlaceholders))#False
   #named placeholders buggy because not properly supported for QSPATIALITE driver.
   #use positional instead?
   #fuck sql injection risk. just use replace.


def prepareQuery(query , db=None):
    if db is None:
        db = defaultDb()
    query = query.replace("\n",' ')    
    q = QSqlQuery(db)    
    if not q.prepare(query):
        raise queryPrepareError(q)
    return q


def runQuery(query : str ,db = None,values = {} , printQuery = False , forwardOnly = False):
    if db is None:
        db = defaultDb()
  #  query = query.replace("\n",' ')
    q = QSqlQuery(db)
    q.setForwardOnly(forwardOnly)
    if not q.prepare(query):
        raise queryPrepareError(q)
    if isinstance(values,dict):
        for k in values:
            q.bindValue(k,values[k])
    if printQuery:
        t = query
        for k,v in values.items():
            t = t.replace(k,str(v))
        print(t)
    if not q.exec():
        print(q.boundValues())
        raise queryError(q)
    return q


import shutil


#copy to file. keeps using same db afterwards.
def saveToFile(file):
   if dbFile == ':memory:':
        runQuery(query = "vacuum main into :file".replace(':file',file))#error transaction in progress... with non memory database
   else:
       shutil.copy2(dbFile, file)



#change QSqlDatabase?
#slightly quicker
#vs copy tables?
#good if using in memory database

def loadFile(dbFile : str):
    db = defaultDb()
    db.transaction()
    try:
        runQuery(query = "DETACH DATABASE 'db2'",db = db)
    except Exception:
        pass
    
    runQuery("ATTACH DATABASE ':file' AS db2".replace(':file',dbFile),db=db)
    runQuery("delete from images",db = db)
    runQuery('insert into images(frame_id,original_file,image_type) select frame_id,original_file,image_type from db2.images',db=db)
    runQuery("delete from runs",db=db)
    runQuery('insert into runs(start_frame,end_frame,correction_start_m,correction_end_m,correction_start_offset,correction_end_offset) select start_frame,end_frame,correction_start_m,correction_end_m,correction_start_offset,correction_end_offset from db2.runs',db=db)
    runQuery("delete from original_points",db=db)
    runQuery('insert into original_points(m,pt) select m,pt from db2.original_points',db=db)
    db.commit()
   # runQuery("DETACH DATABASE 'db2'",db=db)


def hasGps(db=None) -> bool:
    q = runQuery('select count(m) from original_points',db)
    while q.next():
        return q.value(0) > 0


def vacuum():
    runQuery('vacuum')



#want to call this at least once to avoid driver not loaded error.
def createDb(file = dbFile,name = 'image_loader') -> QSqlDatabase:
    db = QSqlDatabase.addDatabase("QSPATIALITE",name)
    db.close()
    db.setDatabaseName(file)
    if not db.open():
        raise ValueError('could not open database')
#    initDb(db)
    return db


#def sqliteVersion():
 #   q = runQuery('select sqlite_version()')
  #  return q.value(0)


#->int
def crackCount() -> int:
    q = runQuery('select count(crack_id) from cracks')
    while q.next():
        return q.value(0)

#->int
def rutCount() -> int:
    q = runQuery('select count(frame) from rut')
    while q.next():
        return q.value(0)
    
#->int
def faultingCount() -> int:
    q = runQuery('select count(frame) from transverse_joint_faulting')
    while q.next():
        return q.value(0)


def clear():
    clearDistresses()
    

def clearDistresses():
    db = defaultDb()
    db.transaction()
    runQuery('delete from transverse_joint_faulting',db=db)
    runQuery('delete from cracks',db=db)
    runQuery('delete from rut',db=db)
    db.commit()
    try:
        runQuery('VACUUM')#reclaim space
    except:
        pass
    