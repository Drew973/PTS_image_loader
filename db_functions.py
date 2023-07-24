# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 14:28:37 2023

@author: Drew.Bennett

geopackage for easier debugging?
filelocks?


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





def runQuery(query,db = None,values = {}):
    
    if db is None:
        db = defaultDb()
        
    query = query.replace("\n",' ')
    
    if isinstance(values,dict):
        for k in values:
            query = query.replace(k,str(values[k]))
            #q.bindValue(k,values[k])
            #print(values)
            #print(q.boundValues())
            
    #    for v in values:
         #   i = query.index(v)
         #   print('index',i)
          #  query=query.replace()

#    print(query)

    q = QSqlQuery(db)    
    if not q.prepare(query):
        raise queryPrepareError(q)
        
  #  if isinstance(values,list):
     #   for i,v in enumerate(values):
            #q.bindValue(i,v)
        #    q.addBindValue(v)
        
    if not q.exec():
        print(q.boundValues())
        raise queryError(q)
        
    return q

import shutil

def saveToFile(file):
   if dbFile() == ':memory:':
        runQuery(query = "vacuum main into ':file'".replace(':file',file))#error transaction in progress... with non memory database
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
    runQuery('insert into images(image_id,run,original_file,image_type,marked) select image_id,run,original_file,image_type,marked from db2.images',db=db)
    runQuery("delete from corrections",db=db)
    runQuery('insert into corrections(run,chainage,x_offset,y_offset,new_x,new_y) select run,chainage,x_offset,y_offset,new_x,new_y from db2.corrections',db=db)
    runQuery("delete from points",db=db)
    runQuery('insert into points(m,x,y,next_m,last_m,corrected_x,corrected_y) select m,x,y,next_m,last_m,corrected_x,corrected_y from db2.points',db=db)
    db.commit()
   # runQuery("DETACH DATABASE 'db2'",db=db)


def hasGps(db=None):
    q = runQuery('select count(m) from points',db)
    while q.next():
        return q.value(0) > 0


def initDb(db):
    db.transaction()
    
    script = '''
    SELECT InitSpatialMetaData();
    
   create table if not exists images 
            ( 
                pk INTEGER PRIMARY KEY
                ,image_id INTEGER
                ,run text default ''
                ,original_file text
                ,new_file text
                ,image_type text
                ,marked bool default false
                ,original_start_chainage float GENERATED ALWAYS AS (image_id*5) VIRTUAL
                ,original_end_chainage float GENERATED ALWAYS AS (image_id*5+5) VIRTUAL
             );
      
	create table if not exists corrections
            ( 
                 pk INTEGER PRIMARY KEY
                 ,run text default ''
                 ,chainage DECIMAL(9,3) unique not null
				 ,new_x float
				 ,new_y float
				 ,x_offset float
				 ,y_offset float
             );
            
    create table if not exists points(
		pk INTEGER PRIMARY KEY
        ,m float not null unique
        ,x float
        ,y float
        ,corrected_x float
        ,corrected_y float        
        ,next_m float
        ,next_pk int
        ,last_m float
        ,pt generated as (makePointM(x,y,m))
        ,corrected_pt generated as (makePointM(corrected_x,corrected_y,m))
        );    
  
   CREATE INDEX IF NOT EXISTS m_index on points(m);
   create index if not exists next_m_ind on points(next_m);
  
   
create view if not exists lines_view as
select points.m as start_m
,points.next_m as end_m
,makeline(points.pt,points2.pt) as line
,makeline(points.corrected_pt,points2.corrected_pt) as corrected_line
,points.corrected_x as corrected_start_x
,points.corrected_y as corrected_start_y
from points inner join points as points2
on points2.m = points.next_m;

create view if not exists corrections_view as
select pk,run,chainage,new_x,new_y,x_offset,y_offset
,st_x(Line_Interpolate_Point(corrected_line,(chainage-start_m)/(end_m-start_m))) + x_offset as current_x
,st_y(Line_Interpolate_Point(corrected_line,(chainage-start_m)/(end_m-start_m))) + y_offset as current_y
,new_x-st_x(Line_Interpolate_Point(line,(chainage-start_m)/(end_m-start_m))) - x_offset as x_shift
,new_y - st_y(Line_Interpolate_Point(line,(chainage-start_m)/(end_m-start_m))) - y_offset as y_shift
from corrections left join lines_view on start_m <= chainage and chainage < end_m;

create view if not exists cv as
select chainage,x_shift,y_shift 
,lead(chainage) over (order by chainage) as next_ch
,lag(chainage) over (order by chainage) as last_ch
,lead(x_shift) over (order by chainage)	as next_xs
,lead(y_shift) over (order by chainage) as next_ys
from corrections_view;

create view if not exists points_view as
select pk
,m
,COALESCE(x+x_shift+(next_xs-x_shift)*(m-chainage)/(next_ch-chainage),x+x_shift,x) as corrected_x
,COALESCE(y+y_shift+(next_ys-y_shift)*(m-chainage)/(next_ch-chainage),y+y_shift,y) as corrected_y
from points left join cv on chainage<m and m<next_ch
or next_ch is null and m>=chainage
or last_ch is null and m<=chainage
;

create view if not exists images_view as
select original_file,
image_id,
makeLine(MakePointM(corrected_x,corrected_y,m)) as center_line
from images
inner join points_view on marked and image_id*5<=m and m<=image_id*5+5
group by original_file
order by m;

    '''
    
    for q in script.split(';'):
        q = q.strip()
        if q:
            runQuery(query = q,db = db)
    db.commit()

    
import csv
from qgis.core import QgsPointXY,QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject



#todo:
#PRAGMA synchronous = OFF
#PRAGMA journal_mode = MEMORY

def loadGps(file,db=None):
    if db is None:
        db = defaultDb()

    #do tranform in QGIS. ST_TransformXY slow and buggy.
    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),QgsCoordinateReferenceSystem('EPSG:27700'),QgsProject.instance())
    db.transaction()
        
    #runQuery(db=db,query='delete from gps')
    runQuery(db=db,query='delete from points')
    
    q = QSqlQuery(db)
    if not q.prepare('insert into points(m,x,y) values(:m,:x,:y)'):
        raise queryError(q)
    
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        
        for i,d in enumerate(reader):
            pt = transform.transform(QgsPointXY(float(d['Longitude (deg)']),float(d['Latitude (deg)'])))
            m = float(d['Chainage (km)'])*1000
            q.bindValue(':m',m)
            q.bindValue(':x',pt.x())
            q.bindValue(':y',pt.y())
            if not q.exec():
                print(q.boundValues())
                raise queryError(q)
    
    q = '''with a as (
    select pk,lead(pk) over (order by m) as next_pk,lead(m) over (order by m) as next_m,lag(m) over (order by m) as last_m from points
    )
    update points set next_pk = a.next_pk,next_m=a.next_m,last_m = a.last_m from a where a.pk = points.pk'''
    runQuery(query=q,db=db)
    db.commit()



#update corrected_x and corrected_y columns of points using corrections.
def correctGps():
    s = '''
update points set corrected_x = x,corrected_y=y;
update points set corrected_x = points_view.corrected_x,corrected_y=points_view.corrected_y from points_view where points_view.m=points.m;
'''
   
    for q in s.split(';'):
        q = q.strip()
        if q:
     #       print('query',q)
            runQuery(query = q)

#start and end can be float,numpy array...
#def interpolate(start,startM,end,endM,m):
  #  frac = (m-startM)/abs(endM-startM)
   # return start + frac*(end-start)
    
 #print(interpolate(0,0,100,10,2))#50   


chainageQuery = '''
select start_m+(end_m-start_m)*Line_Locate_Point(line,makePoint(:x,:y)) as corrected_chainage
from lines_view where
end_m >= coalesce((select min(original_start_chainage)-200 from images where run = ''),(select min(m) from points))
and start_m <= coalesce((select max(original_end_chainage)+200 from images where run = ''),(select max(m) from points))
and abs(corrected_start_x-:x) < 50
and abs(corrected_start_y-:y) < 50
order by st_distance(line,makePoint(:x,:y))
limit 1
'''
#->(chainage:float,offset:float) or None
def getChainage(run,x,y,db):   
    q = runQuery(query=chainageQuery,values={':x':x,':y':y,':run':run,':dist':50},db=db)
    while q.next():
        if isinstance(q.value(0),float):
            return q.value(0)
    print('no chainage found for run "{run}" ({x},{y})'.format(x=x,y=y,run=run))
    return -1
    

correctedChainageQuery = '''
select start_m+(end_m-start_m)*Line_Locate_Point(corrected_line,makePoint(:x,:y)) as corrected_chainage
from lines_view where
end_m >= coalesce((select min(original_start_chainage)-200 from images where run = ':run'),(select min(m) from points))
and start_m <= coalesce((select max(original_end_chainage)+200 from images where run = ':run'),(select max(m) from points))
and abs(corrected_start_x-:x) < 50
and abs(corrected_start_y-:y) < 50
order by st_distance(corrected_line,makePoint(:x,:y))
limit 1
'''
def getCorrectedChainage(run,x,y,db):
    q = runQuery(query=correctedChainageQuery,values={':x':x,':y':y,':run':run,':dist':50},db=db)
    while q.next():
        if isinstance(q.value(0),float):
            return q.value(0)
    print('no chainage found for run "{run}" ({x},{y})'.format(x=x,y=y,run=run))
    return -1


pointQuery = '''select st_x(Line_Interpolate_Point(line,(:ch-start_m)/(end_m-start_m))),st_y(Line_Interpolate_Point(line,(:ch-start_m)/(end_m-start_m)))
from lines_view where start_m <= :ch and :ch <=end_m'''
# -> QgsPointXY
def getPoint(chainage,db):
        q = runQuery(query=pointQuery,db = db,values= {':ch':float(chainage)})
        while q.next():
            if isinstance(q.value(0),float) and isinstance(q.value(1),float):
                return QgsPointXY(q.value(0),q.value(1))
        return QgsPointXY()
    
    
correctedPointQuery = '''select st_x(Line_Interpolate_Point(corrected_line,(:ch-start_m)/(end_m-start_m))),st_y(Line_Interpolate_Point(corrected_line,(:ch-start_m)/(end_m-start_m)))
from lines_view where start_m <= :ch and :ch <=end_m'''
def getCorrectedPoint(chainage,db):
        q = runQuery(query=correctedPointQuery,db = db,values= {':ch':float(chainage)})
        while q.next():
            if isinstance(q.value(0),float) and isinstance(q.value(1),float):
                return QgsPointXY(q.value(0),q.value(1))
        return QgsPointXY()    
    
    
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


