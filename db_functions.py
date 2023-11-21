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
import os
from PyQt5.QtSql import QSqlDatabase,QSqlQuery


class queryError(Exception):
    def __init__(self,query):
        super().__init__('error executing query {q}:{err}'.format(q = query.lastQuery(),err = query.lastError().text()))


class queryPrepareError(Exception):
    def __init__(self,query):
        super().__init__('error preparing query {q}:{err}'.format(q = query.lastQuery(),err = query.lastError().text()))
        
        
        
def defaultDb():
    return QSqlDatabase.database('image_loader')        
        

#from PyQt5.QtSql import QSqlDriver
   #print('has named placeholders',db.driver().hasFeature(QSqlDriver.NamedPlaceholders))#False
   #named placeholders buggy because not properly supported for QSPATIALITE driver.
   #use positional instead?
   #fuck sql injection risk. just use replace.


def runQuery(query,db = None,values = {},printQuery=False):
    
    if db is None:
        db = defaultDb()
        
    query = query.replace("\n",' ')

    q = QSqlQuery(db)    
    if not q.prepare(query):
        raise queryPrepareError(q)
        
    if isinstance(values,dict):
        for k in values:
            #query = query.replace(k,str(values[k]))
            q.bindValue(k,values[k])
              
  #  if isinstance(values,list):
     #   for i,v in enumerate(values):
            #q.bindValue(i,v)
        #    q.addBindValue(v)
        
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

def saveToFile(file):
   if dbFile() == ':memory:':
        runQuery(query = "vacuum main into :file".replace(':file',file))#error transaction in progress... with non memory database
   else:
       shutil.copy2(dbFile(), file)


def loadFile(dbFile):
    db = defaultDb()
    db.transaction()
    try:
        runQuery(query = "DETACH DATABASE 'db2'",db = db)
    except Exception:
        pass
    runQuery("ATTACH DATABASE ':file' AS db2".replace(':file',dbFile),db=db)
    runQuery("delete from images",db = db)
    runQuery('insert into images(frame_id,run,original_file,image_type,marked) select frame_id,run,original_file,image_type,marked from db2.images',db=db)
    runQuery("delete from corrections",db=db)
    runQuery('insert into corrections(run,chainage,x_offset,y_offset,new_x,new_y) select run,chainage,x_offset,y_offset,new_x,new_y from db2.corrections',db=db)
    runQuery("delete from original_points",db=db)
    runQuery('insert into original_points(m,pt) select m,pt from db2.points',db=db)
    db.commit()
   # runQuery("DETACH DATABASE 'db2'",db=db)


def hasGps(db=None):
    q = runQuery('select count(m) from original_points',db)
    while q.next():
        return q.value(0) > 0


#store m in z. can use for interpolating

def initDb(db):
    db.transaction()
    script = '''
    SELECT InitSpatialMetaData();
    
    create table if not exists runs
    (
    	pk INTEGER PRIMARY KEY
    	,start_chainage float default 0.0
    	,end_chainage float default 0.0
    	,chainage_correction float default 0.0
    	,left_offset float default 0.0
    );
    
    create view if not exists runs_view as select ROW_NUMBER() over (order by start_chainage,end_chainage) as number,pk
    ,start_chainage,end_chainage,chainage_correction,left_offset from runs;

    
   create table if not exists images
            ( 
                pk INTEGER PRIMARY KEY
                ,frame_id INTEGER
                ,original_file text
                ,new_file text
                ,image_type text
                ,marked bool default false
             );
      
	create table if not exists corrections
            ( 
                 pk INTEGER PRIMARY KEY
                 ,run text default ''
                 ,frame_id int not null
				 ,line int
				 ,pixel int
				 ,new_x float
				 ,new_y float
             );
            
   create view if not exists corrections_m as select pk,5.0*(frame_id-line/1250) as m,
   4.0*0.5-pixel*4.0/1038 as left_offset,makePoint(new_x,new_y) as pt from corrections;

create view if not exists images_view as
select number as run,chainage_correction,left_offset,images.pk,frame_id,original_file,image_type,marked from images
            inner join runs_view on frame_id*5+5 >= start_chainage and frame_id*5 <= end_chainage;
            
create table if not exists original_points(
    		id INTEGER PRIMARY KEY
            ,m float
            ,next_id int
            ,next_m float
            );
 
    SELECT AddGeometryColumn('original_points' , 'pt', 27700, 'POINT', 'XY');
    create index if not exists original_points_m on original_points(m);

 create table if not exists corrected_points(
    		id INTEGER PRIMARY KEY
            ,m float
            ,next_id int
            );
    SELECT AddGeometryColumn('corrected_points' , 'pt', 27700, 'POINT', 'XY');
    create index if not exists corrected_points_m on corrected_points(m);


    drop table if exists pos;
    create table if not exists pos (pixel float,line float);
    insert into pos (pixel,line) values (519,0),(519,625),(519,1250),(516,200),(525,400);

   create view if not exists lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from original_points as c
    inner join original_points as next 
    on next.id = c.id+1;
    
   create view if not exists corrected_lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from corrected_points as c
    inner join corrected_points as next 
    on next.id = c.id+1;

create view if not exists gcp as
select frame_id,pixel,line,
5.0*(frame_id -line/1250) as m 

,(select Line_Interpolate_Point(corrected_lines.line,(5.0*(frame_id -pos.line/1250)-start_m)/(end_m-start_m))
        from corrected_lines where start_m <= 5.0*(frame_id -pos.line/1250) and end_m >= 5.0*(frame_id -pos.line/1250)
		limit 1
) as pt
from (select distinct frame_id from images where marked) frames inner join pos;

    
    create view if not exists lines_5 as
    select s,e,makeLine(pt) as line from
    (select cast(id/5.0 as int)*5 as s,cast(id/5.0 as int)*5+5 as e from original_points as e group by s,e)
    inner join original_points on s<=id and id<=e
    group by s
    order by m;
    
    '''

    
    for q in script.split(';'):
        q = q.strip()
        if q:
            runQuery(query = q,db = db)
    db.commit()

    
import csv

    
def loadCorrections(file):
    db = QSqlDatabase.database('image_loader')
    db.transaction()
    q = QSqlQuery(db)
    if not q.prepare('insert into corrections(run,original_chainage,original_offset,new_chainage,new_offset) values (:run,:original_chainage,:origonal_offset,:new_chainage,:new_offset)'):
        raise queryError(q)
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.lower().replace('_','') for name in reader.fieldnames]#lower case keys/fieldnames                 
        #correction at start of each run
        for r in reader:
            #print(r)
            q.bindValue(':run',r['runid'])
            q.bindValue(':original_chainage',int(r['fromframe'])*5)
            q.bindValue(':new_chainage',int(r['fromframe'])*5 + float(r['chainage']))
            q.bindValue(':origonal_offset',0)
            q.bindValue(':new_offset',r['offset'])
            if not q.exec():
                print(q.boundValues())
                raise queryError(q)
    db.commit()
    
    
def hasMarked(run):
    q = runQuery(query = "select max(marked) = 1 from images where run = ':run'",values = {':run':run})
    while q.next():
        return bool(q.value(1))

    
def dbFile():
  #  return ':memory:'        
    return os.path.join(os.path.dirname(__file__),'images.db')


def createDb(file = dbFile()):
    db = QSqlDatabase.addDatabase("QSPATIALITE",'image_loader')
    db.close()
    db.setDatabaseName(file)
    if not db.open():
        raise ValueError('could not open database')
    initDb(db)
    return db


def sqliteVersion():
    q = runQuery('select sqlite_version()')
    return q.value(0)



def runChainages(run):
    
    s = 0.0
    e = 0.0
    q = runQuery(query = "select m from run_changes where next_run  = :run",values = {':run':run})
    while q.next():
        s = q.value(0)
        break
    
    q = runQuery(query = "select m from run_changes where last_run  = :run",values = {':run':run})
    while q.next():
        e = q.value(0)
        break
    
    return (s,e)


def setStartChainage(run,m):
    runQuery(query = "INSERT OR REPLACE INTO run_changes(m,next_run values (m = :m where next_run  = :run",values = {':run':run,':m':m})


def setEndChainage(run,m):
    runQuery(query = "update run_changes set m = :m where last_run  = :run",values = {':run':run,':m':m})


if __name__ == '__console__':
    print(sqliteVersion)