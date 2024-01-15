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


def prepareQuery(query,db=None):
    if db is None:
        db = defaultDb()
    query = query.replace("\n",' ')    
    q = QSqlQuery(db)    
    if not q.prepare(query):
        raise queryPrepareError(q)
    return q


def runQuery(query,db = None,values = {},printQuery=False):
    if db is None:
        db = defaultDb()
  #  query = query.replace("\n",' ')
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
    runQuery('insert into images(frame_id,run,original_file,image_type) select frame_id,run,original_file,image_type from db2.images',db=db)
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
    	,start_frame int default 0
    	,end_frame int default 0
    );
    
    create view if not exists runs_view as select ROW_NUMBER() over (order by start_frame,end_frame) as number,pk
    ,start_frame,end_frame from runs;

    
   create table if not exists images
            ( 
                pk INTEGER PRIMARY KEY
                ,frame_id INTEGER
                ,original_file text unique
                ,new_file text
                ,image_type text
             );
      
	create table if not exists corrections
            ( 
                 pk INTEGER PRIMARY KEY
                 ,frame_id int not null
				 ,line int default 0
				 ,pixel int default 0
				 ,new_x float
				 ,new_y float
				 ,x_shift float
				 ,y_shift float
             );
			 
create index if not exists corrections_frame on corrections(frame_id);
            
create view if not exists corrections_m as select pk,5.0*(frame_id-line/1250) as m,
4.0*0.5-pixel*4.0/1038 as left_offset,makePoint(new_x,new_y) as pt from corrections;

create view if not exists images_view as
select pk,original_file,image_type,frame_id
,(select number from runs_view where start_frame<=frame_id and end_frame >= frame_id order by number limit 1) as run
from images;
            
create table if not exists original_points(
    		id INTEGER PRIMARY KEY
            ,m float
            ,next_id int
            ,next_m float
            );
 
SELECT AddGeometryColumn('original_points' , 'pt', 27700, 'POINT', 'XY');
create index if not exists original_points_m on original_points(m);

create table if not exists transforms
(
	start_m float
	,end_m float
	,t00 float default 1.0-- x scale
	,t01 float default 0.0 --rotation
	,t02 float-- x shift
	,t10 float default 0.0 -- rotation
	,t11 float default 1.0 -- y scale
	,t12 float -- y shift
);
create index if not exists start_m_ind on transforms(start_m);
create index if not exists end_m_ind on transforms(end_m);


create view if not exists corrected_points as
select id,m,next_id,next_m
,makePoint(
st_x(pt)*t00 + t01*st_y(pt) + t02
,st_x(pt)*t10 + t11*st_y(pt) + t12
,27700) as pt
 from original_points inner join transforms on m >= start_m and m < end_m;


drop table if exists pos;
create table if not exists pos (pixel float,line float);
insert into pos (pixel,line) values (519,0),(519,625),(519,1250),(516,200),(525,400);

   create view if not exists original_lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from original_points as c
    inner join original_points as next 
    on next.id = c.id+1;
    
   create view if not exists corrected_lines as
    select c.id,c.m as start_m,next.m as end_m,makeLine(makePointz(st_x(c.pt),st_y(c.pt),c.m),makePointz(st_x(next.pt),st_y(next.pt),next.m)) as line from corrected_points as c
    inner join corrected_points as next 
    on next.id = c.id+1;
    
    create view if not exists lines_5 as
    select s,e,makeLine(pt) as line from
    (select cast(id/5.0 as int)*5 as s,cast(id/5.0 as int)*5+5 as e from original_points as e group by s,e)
    inner join original_points on s<=id and id<=e
    group by s
    order by m;
    
create view if not exists interpolate_corrections as
select m,5*(frame_id-line/1250) as next_m
,c.x_shift,c.y_shift
,n.x_shift as next_x_shift,n.y_shift as next_y_shift from
(select 5*(frame_id-line/1250) as m
,lead(pk) over (order by 5*(frame_id-line/1250)) as next
,x_shift
,y_shift
from corrections) c
inner join corrections as n
on n.pk = c.next;

CREATE VIEW if not exists corrected_view as select id,p.m,p.next_m,p.next_id
,makePoint(
st_x(pt) + x_shift + (p.m-c.m)*(next_x_shift-x_shift)/(c.next_m-c.m)
,st_y(pt) + y_shift + (p.m-c.m)*(next_y_shift-y_shift)/(c.next_m-c.m)
,27700) as point
from original_points as p inner join interpolate_corrections as c on c.m < p.m and p.m < c.next_m
union
select id,p.m,p.next_m,p.next_id
,makePoint(st_x(pt)+x_shift,
st_y(pt) + y_shift
,27700)
from 
(select m,x_shift,y_shift from interpolate_corrections order by m limit 1) mi
inner join original_points as p on p.m <= mi.m
union
select id,p.m,p.next_m,p.next_id
,makePoint(st_x(pt)+next_x_shift,
st_y(pt) + next_y_shift
,27700)
from 
(select next_m,next_x_shift,next_y_shift from interpolate_corrections order by m desc limit 1) mi
inner join original_points as p on p.m >= mi.next_m;



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