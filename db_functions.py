# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 14:28:37 2023

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlDatabase,QSqlQuery
#ST_LineMerge(ST_Union(ST_Locate_Between_Measures))





class queryError(Exception):
    def __init__(self,query):
        super().__init__('error executing query {q}:{err}'.format(q = query.lastQuery(),err = query.lastError().text()))


class queryPrepareError(Exception):
    def __init__(self,query):
        super().__init__('error preparing query {q}:{err}'.format(q = query.lastQuery(),err = query.lastError().text()))
        
        
        
def runQuery(query,db = None,values = {}):
    
    if db is None:
        db = QSqlDatabase.database('image_loader')
        
    q = QSqlQuery(db)
    if not q.prepare(query):
        raise queryError(q)
    
    for k in values:
        q.bindValue(k,values[k])
      
    
    if not q.exec():
        print(q.boundValues())
        raise queryError(q)
        
    return q
        

def hasGps(db=None):
    q = runQuery('select count(pk) from gps',db)
    q.next()
    return q.value(0) > 0
    
        
def initDb(db):
    db.transaction()
    
    
    runQuery(db=db,query='SELECT InitSpatialMetaData();')
    
   # runQuery('drop table if exists gps;')

    q = '''create table if not exists gps 
            ( pk INTEGER PRIMARY KEY
             ,start_m float NOT NULL
             ,end_m float NOT NULL
            )
        '''
    runQuery(db=db,query=q)    
    
    runQuery(db=db,query='CREATE INDEX IF NOT EXISTS start_m_index on gps(start_m)')
    runQuery(db=db,query='CREATE INDEX IF NOT EXISTS end_m_index on gps(end_m)')    
    runQuery(db=db,query="SELECT AddGeometryColumn('gps', 'line',27700, 'Linestring', 'XY')")

    
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
    
    runQuery(db=db,query="SELECT AddGeometryColumn('images', 'line',27700, 'Linestring', 'XY')")

    
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
    
create view if not exists corrections_view as
select m
,a.run

,coalesce(
--prev.y + (x-prev.x)*(next.y-prev.y)/(next.x - prev.x)
prev.new_offset - prev.original_offset + (m-prev.original_chainage)*(next.offset_shift - prev.offset_shift)/(next.original_chainage-prev.original_chainage)
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
    create view if not exists images2 as
select original_file
,image_id*5
,image_id*5+s.chainage_diff as start_m
,image_id*5+5+e.chainage_diff as end_m
,s.offset_diff as left_offset
 from images 
inner join corrections_view as s
on marked and images.run = s.run and image_id*5 = s.m
inner join corrections_view as e
on marked and images.run = e.run and image_id*5+5 = e.m
    '''
    
    runQuery(db=db,query=q)
    
    
    q = '''    
    create view if not exists images_view as
select original_file,
ST_OffsetCurve(ST_Line_Substring(ST_LineMerge(ST_Collect(line))
,case when images2.start_m > min(gps.start_m) then 
	(images2.start_m - min(gps.start_m))/abs(max(gps.end_m)-min(gps.start_m))
else 0
end

,case when max(gps.end_m)>images2.end_m then 
	(images2.end_m - min(gps.start_m))/abs(max(gps.end_m)-min(gps.start_m))
else 1
end
),left_offset
)
 as line
from images2 left join gps on gps.end_m>images2.start_m and gps.start_m<images2.end_m group by original_file

    '''
    
    runQuery(db=db,query=q)
    
    q = '''
    create table if not exists points(
        m float
        ,x float
        ,y float
        )    
    '''
    runQuery(db=db,query=q)
    
    runQuery(db=db,query='CREATE INDEX IF NOT EXISTS m_index on points(m)')

    db.commit()
    
    
import csv
from qgis.core import QgsPointXY,QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject



#todo:
 #   make this more efficient. something like
    #0.2 s to load into points via QSqlQuery.

#could do something like this    
  # sqlite3 "C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\images.db" -cmd ".mode csv" ".import C:\\Users\\drew.bennett\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\image_loader\\test\\1_007\\MFV1_007-rutacd-1.csv test_gps"
 #in subprocess. probably not worthwhile
 #to group points use st_makeLine and group by floor(m/n)



#
#PRAGMA synchronous = OFF
#PRAGMA journal_mode = MEMORY

def loadGps(file,db):
    
 #   s = '\\'[0] #making single '\' charactor shouldn't be this complicated
  #  
   # command = 'sqlite3 "{dbFile}" -cmd ".mode csv" ".import {f} temp_gps"'.format(dbFile = db.DatabaseName(),f = file.replace(s,s+s))
 #   subprocess.run(command)
        
    #do tranform in QGIS. ST_TransformXY slow and buggy.
    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),QgsCoordinateReferenceSystem('EPSG:27700'),QgsProject.instance())
    db.transaction()
        
  #  return
    runQuery(db=db,query='delete from gps')
    
   # runQuery(db=db,query='drop table if exists points')
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
select 
m
,x
,y
,lead(rowid) over (order by m) as next_pk
from points
)
insert into gps(start_m,end_m,line)
select a.m,next.m,MakeLine(MakePoint(a.x,a.y,27700),MakePoint(next.x,next.y,27700)) from a inner join points as next on next_pk = next.rowid
'''
    runQuery(query=q,db=db)    
 
    db.commit()

#MakePointM	

import numpy


def toVector(point):
    return numpy.array([point.x(),point.y()])


#start and end can be float,numpy array...
def interpolate(start,startM,end,endM,m):
    frac = (m-startM)/abs(endM-startM)
    return start + frac*(end-start)
    
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
find closest chainage & offset of closest point within run
Cases where point past end of line.
define offset as perpendicular component of shortest line. usually same as length.

perpendicular component = shortestline x geom / |geom|
--doesnt use spatial index. spatial index in spatialite is PITA...
'''


chainageQuery = '''
select chainage
,st_x(st_endPoint(v))-st_x(st_startPoint(v)) as x1
,st_y(st_endPoint(v))-st_y(st_startPoint(v)) as y1
,st_x(st_endPoint(line))-st_x(st_startPoint(line)) as x2
,st_y(st_endPoint(line))-st_y(st_startPoint(line)) as y2

from
(select
start_m+(end_m-start_m)*Line_Locate_Point(line,pt) as chainage
,line
,ST_ShortestLine(pt,line) as v
from
(select MakePoint({x},{y}) as pt) point
inner join gps on
start_m <= coalesce((select max(original_end_chainage) from images where run = '{run}'),(select max(end_m) from gps))
and end_m>= coalesce((select min(original_start_chainage) from images where run = '{run}'),(select min(start_m) from gps))
and ST_Distance(MakePoint({x},{y}),line)<50
order by ST_Distance(pt,line)
limit 1
)
'''


#->(chainage,offset) or None
def getChainage(run,x,y,db):   
    q = runQuery(query=chainageQuery.format(x=x,y=y,run=run),db=db)
    while q.next():
        shortest = numpy.array([q.value(1),q.value(2)])#shortest line as vector
        geom = numpy.array([q.value(3),q.value(4)])#gps geometry as vector
        geomLen = numpy.sqrt(numpy.sum(geom**2))
        return (q.value(0),numpy.cross(shortest,geom)/geomLen)
      
        
    
def getPoint(chainage,offset,db):
        
        #bug in spatialite ST_OffsetCurve. low offsets != 0 produce empty linestring
        #left positive
        q = '''select st_x(Line_Interpolate_Point(ST_OffsetCurve(line,round(:off,6)),(:ch - start_m)/abs(end_m-start_m)))
        ,st_y(Line_Interpolate_Point(ST_OffsetCurve(line,round(:off,6)),(:ch - start_m)/abs(end_m-start_m)))
        from gps
        where start_m <= :ch and end_m >= :ch
        limit 1
        '''
        #print('getPoint',q)
        
        values = {':ch':float(chainage),':off':float(offset)}
        
        q = runQuery(query=q,db = db,values=values)
        
       # print('bv',q.boundValues())
        while q.next():
            return QgsPointXY(q.value(0),q.value(1))
        print('no points')
        return QgsPointXY()
    
    

def loadCorrections(file):
    
    db = QSqlDatabase.database('image_loader')
    db.transaction()

    q = QSqlQuery(db)
    if not q.prepare('insert into corrections(original_chainage,original_offset,new_chainage,new_offset) values (:original_chainage,:origonal_offset,:new_chainage,:new_offset)'):
        raise queryError(q)



    with open(file,'r') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.lower().replace('_','') for name in reader.fieldnames]#lower case keys/fieldnames                 

        #correction at start and end of each run
        for r in reader:
            #print(r)
            q.bindValue(':original_chainage',int(r['fromframe'])*5)
            q.bindValue(':new_chainage',int(r['fromframe'])*5 + float(r['chainage']))
            q.bindValue(':origonal_offset',0)
            q.bindValue(':new_offset',r['offset'])

            if not q.exec():
                print(q.boundValues())
                raise queryError(q)
    
            q.bindValue(':original_chainage',int(r['toframe'])*5)
            q.bindValue(':new_chainage',int(r['toframe'])*5 + float(r['chainage']))
            q.bindValue(':origonal_offset',0)
            q.bindValue(':new_offset',r['offset'])

            if not q.exec():
                print(q.boundValues())
                raise queryError(q)
    
    db.commit()



def createDb(file = ':memory:'):    
    db = QSqlDatabase.addDatabase("QSPATIALITE",'image_loader')
    db.setDatabaseName(file)
    if not db.open():
        raise ValueError('could not open database')
    initDb(db)
    return db



import unittest
import os
from image_loader import test

class testDbFunctions(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        createDb(file = os.path.join(test.testFolder,'test.db'))
        
        
    def setUp(self):
        pass        

    @classmethod
    def tearDownClass(cls):
        QSqlDatabase.database('image_loader').close()
    
    
    def testLoadCorrections(self):
        file = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\MFV1_006 Coordinate Corrections.csv'
        loadCorrections(file=file)


    def testLoadGps(self):
        loadGps(file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv'),db = QSqlDatabase.database('image_loader'))
        self.assertTrue(hasGps())


if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testDbFunctions)
    unittest.TextTestRunner().run(suite)
    