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
        raise queryError(q)
        
        

        
        
  #  if isinstance(values,list):
     #   for i,v in enumerate(values):
            #q.bindValue(i,v)
        #    q.addBindValue(v)
    

        
    if not q.exec():
        print(q.boundValues())
        raise queryError(q)
        
    return q
        
#save to file.
#"vacuum main into 'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\saved.db'"
def saveToFile(file):
    runQuery(query = "vacuum main into ':file'".replace(':file',file))


def loadFile(dbFile):
    try:
        runQuery("DETACH DATABASE if exists db2".replace(':file',dbFile))
    except Exception:
        pass
    
    runQuery("ATTACH DATABASE ':file' AS db2".replace(':file',dbFile))
    runQuery("delete from images")
    runQuery('insert into images(image_id,run,original_file,image_type,marked) select image_id,run,original_file,image_type,marked from db2.images')
    runQuery("delete from corrections")
    runQuery('insert into corrections(run,original_chainage,new_chainage,original_offset,new_offset) select run,original_chainage,new_chainage,original_offset,new_offset from db2.corrections')
    runQuery("delete from points")
    runQuery('insert into points(m,x,y,next_m,last_m) select m,x,y,next_m,last_m from db2.points')


    
def hasGps(db=None):
    q = runQuery('select count(m) from points',db)
    while q.next():
        return q.value(0) > 0
    
        
def initDb(db):
    db.transaction()
    runQuery(db=db,query='SELECT InitSpatialMetaData()')
  #  runQuery(db=db,query='SELECT EnableGpkgMode()')
   # runQuery(db=db,query='SELECT case when CheckGeoPackageMetaData() then Null else gpkgCreateBaseTables() + gpkgInsertEpsgSRID(27700) end')
    #runQuery(db=db,query="SELECT gpkgInsertEpsgSRID(27700)")


#CheckGeoPackageMetaData	
    q = '''create table if not exists images 
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
             )
        '''
    runQuery(db=db,query=q)
       
    
    q = '''create table if not exists corrections
            ( 
                 pk INTEGER PRIMARY KEY
                 ,run text default ''
                 ,original_chainage float
                 ,original_offset float
                 ,new_chainage float
                 ,new_offset float
				 ,chainage_shift float GENERATED ALWAYS AS (new_chainage - original_chainage) VIRTUAL
				 ,offset_shift float GENERATED ALWAYS AS (new_offset - original_offset) VIRTUAL
             )
        '''
    runQuery(db=db,query=q)
    
    q = '''
    create table if not exists points(
        m float not null unique
        ,x float
        ,y float
        ,next_m float
        ,next_pk int
        ,last_m float
        ,pt generated as (makePointM(x,y,m))
        )    
    '''
    runQuery(db=db,query=q)
    runQuery(db=db,query='CREATE INDEX IF NOT EXISTS m_index on points(m)')
    runQuery(db=db,query='create index if not exists next_m_ind on points(next_m)')
    
  #  runQuery(db=db,query="SELECT gpkgAddGeometryColumn('points', 'point','POINT', 0, 0,27700)")
  #  runQuery(db=db,query="SELECT gpkgAddGeometryTriggers('points', 'point')")

	
    
    q = '''
create view if not exists corrections_view as
select m
,a.run

,coalesce(
--prev.y + (x-prev.x)*(next.y-prev.y)/(next.x - prev.x)
prev.offset_shift + (m-prev.original_chainage)*(next.offset_shift - prev.offset_shift)/(next.original_chainage-prev.original_chainage)
,next.offset_shift
,prev.offset_shift
,0) as offset_diff

,coalesce(
--prev.y + (x-prev.x)*(next.y-prev.y)/(next.x - prev.x)
prev.chainage_shift + (m-prev.original_chainage)*(next.chainage_shift - prev.chainage_shift)/(next.original_chainage-prev.original_chainage)
,next.chainage_shift
,prev.chainage_shift
,0) as chainage_diff

from
(
select run,image_id*5 as m from images where marked
union select run,image_id*5+5 from images where marked
) a

left join corrections as prev on prev.pk = (select pk from corrections where corrections.run=a.run and original_chainage<=m order by original_chainage desc limit 1)
left join corrections as next on next.pk = (select pk from corrections where corrections.run=a.run and original_chainage>=m order by original_chainage asc limit 1)
        '''
    runQuery(db=db,query=q)
    
    
    q = '''
create view if not exists images_with_correction as
select original_file
,image_id*5
,image_id*5+s.chainage_diff as start_m
,image_id*5+5+e.chainage_diff as end_m
,s.offset_diff+2 as left_offset
,s.offset_diff-2 as right_offset
 from images 
inner join corrections_view as s
on marked and images.run = s.run and image_id*5 = s.m
inner join corrections_view as e
on marked and images.run = e.run and image_id*5+5 = e.m
    '''
    
    runQuery(db=db,query=q)#half image width.
    
    
    q = '''    
create view if not exists images_view as
select original_file
,left_offset
,start_m
,end_m
,line_substring(
case when left_offset<0 then 
	st_reverse(st_offsetCurve(makeLine(pt),left_offset))
else
	st_offsetCurve(makeLine(pt),left_offset)
end
,abs(start_m-min(m))/abs(max(m)-min(m))
,abs(end_m-min(m))/abs(max(m)-min(m))
) as left_line

,line_substring(
case when right_offset<0 then 
	st_reverse(st_offsetCurve(makeLine(pt),right_offset))
else
	st_offsetCurve(makeLine(pt),right_offset)
end
,abs(start_m-min(m))/abs(max(m)-min(m))
,abs(end_m-min(m))/abs(max(m)-min(m))
) as right_line

from images_with_correction
inner join points on next_m>=start_m and last_m<=end_m
group by original_file
order by m
    '''
    
    runQuery(db=db,query=q)
    


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
    select rowid as pk,lead(rowid) over (order by m) as next from points
    )
    update points set next_pk = next from a where a.pk = points.rowid
    ;   
    '''
    runQuery(query=q,db=db)    

    q = '''
    with a as (
        select rowid as pk,lead(m) over (order by m) as next from points
        )
        update points set next_m = next from a where a.pk = points.rowid
    '''
    runQuery(query=q,db=db)    

    q = '''
    with a as (
    select rowid as pk,lead(m) over (order by m desc) as last from points
    )
    update points set last_m = last from a where a.pk = points.rowid
	'''
    runQuery(query=q,db=db)    

   # runQuery(db=db,query="update points set point = gpkgMakePoint(x,y,27700)")


    db.commit()

#start and end can be float,numpy array...
#def interpolate(start,startM,end,endM,m):
  #  frac = (m-startM)/abs(endM-startM)
   # return start + frac*(end-start)
    
 #print(interpolate(0,0,100,10,2))#50   


def insertCorrections(corrections,db):
    q = QSqlQuery(db)
    if q.prepare('insert into corrections(run,original_chainage,original_offset,new_chainage,new_offset) values (:run,:original_chainage,:original_offset,:new_chainage,:new_offset)'):
        
        for r in corrections:
            q.bindValue(':run',r['run'])
            q.bindValue(':original_chainage',r['original_chainage'])
            q.bindValue(':new_chainage',r['new_chainage'])
            q.bindValue(':original_offset',r['original_offset'])
            q.bindValue(':new_offset',r['new_offset'])

            if not q.exec():
                print(q.boundValues())
                raise queryError(q)
    else:
        raise queryPrepareError(q)

'''
find closest gps point.
linestring m from last,this,next
offset = distance to line.
find sign of offset by offseting line to left and right and finding nearest to (x,y)
'''


chainageQuery = '''
with nearest as
(
select rowid,next_pk,MakePoint(:x,:y) as p
from points
where ST_Distance(MakePoint(:x,:y),pt)<50
and m >= coalesce((select min(original_start_chainage) from images where run = ':run'),(select min(m) from points))
and m <= coalesce((select max(original_end_chainage) from images where run = ':run'),(select max(m) from points))
order by ST_Distance(MakePoint(:x,:y),MakePoint(x,y))
limit 1
)

,a as
(
select makeline(pt) as line,p from points inner join nearest
on points.next_pk = nearest.rowid or points.rowid = nearest.rowid or points.rowid = nearest.next_pk
order by m
)

, b as
(
select 
p
,line
,round(st_distance(line,p),3) as d from a
)

select ST_InterpolatePoint(line,p) as m
,case when st_distance(p,ST_OffsetCurve(line,d)) < st_distance(p,ST_OffsetCurve(line,-d)) then d else -d end as off
 from b
'''
#->(chainage:float,offset:float) or None
def getChainage(run,x,y,db):   
    q = runQuery(query=chainageQuery,values={':x':x,':y':y,':run':run},db=db)
    while q.next():
        if isinstance(q.value(0),float) and isinstance(q.value(1),float):
            return (q.value(0),q.value(1))
    print('no chainage found for run "{run}" ({x},{y})'.format(x=x,y=y,run=run))

    
    
'''
    chainage often at vertex of gps.
    need to join lines and make offset curve here.
    #strange behavior and bugs in spatialite ST_OffsetCurve.
    low offsets != 0 produce empty linestring
    #reverses direction for negative offsets
    #left positive
'''
    
pointQuery = '''
with nearest as
(
select 
rowid,
next_pk
,round(:off,3) as off
from points
order by abs(m-:m)
limit 1
)

,a as
(
select case when off > 0 then ST_OffsetCurve(makeline(pt),off) when off = 0 then makeline(pt) else st_reverse(ST_OffsetCurve(makeline(pt),off)) end as line,
(:m - min(m))/(max(m)-min(m)) as f
from points inner join nearest
on points.next_pk = nearest.rowid or points.rowid = nearest.rowid or points.rowid = nearest.next_pk
order by m
)
select st_x(Line_Interpolate_Point(line,f)),st_y(Line_Interpolate_Point(line,f)) from a
'''


# -> QgsPointXY
def getPoint(chainage,offset,db):
        q = runQuery(query=pointQuery,db = db,values= {':m':float(chainage),':off':float(offset)})
        while q.next():
            if isinstance(q.value(0),float) and isinstance(q.value(1),float):
                return QgsPointXY(q.value(0),q.value(1))
        print('no points')
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
       #correction at end of each run
       #     q.bindValue(':run',r['runid'])
       #     q.bindValue(':original_chainage',int(r['toframe'])*5)
       #     q.bindValue(':new_chainage',int(r['toframe'])*5 + float(r['chainage']))
       #     q.bindValue(':origonal_offset',0)
      #      q.bindValue(':new_offset',r['offset'])

       #     if not q.exec():
       #         print(q.boundValues())
          #      raise queryError(q)
    
    db.commit()
    
    

def hasMarked(run):
    q = runQuery(query = "select max(marked) = 1 from images where run = ':run'",values = {':run':run})
    while q.next():
        return bool(q.value(1))


    
def dbFile():
  #  return ':memory:'        
    return os.path.join(os.path.dirname(__file__),'images.image_loader_db')


def createDb(file = dbFile()):
    db = QSqlDatabase.addDatabase("QSPATIALITE",'image_loader')
    db.close()
    db.setDatabaseName(file)
    if not db.open():
        raise ValueError('could not open database')
    initDb(db)
    return db


