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
        
        
        
def initDb(db):
    db.transaction()
    
    
    runQuery('SELECT InitSpatialMetaData();')
    
    
    q = '''create table if not exists gps 
            ( pk INTEGER PRIMARY KEY,
             m float NOT NULL,
             last_m float,
             next_m float
            )
        '''
           
    runQuery(q)    
    
    
    runQuery('CREATE INDEX IF NOT EXISTS  m_index on gps(m)')
    
    
    q = "SELECT AddGeometryColumn('gps', 'pt',27700, 'POINT', 'XYM');"
    runQuery(q)

   
    q = '''create table if not exists images 
            ( 
                pk INTEGER PRIMARY KEY,
                image_id INTEGER,
                run text,
                file text,
                marked bool default false,
                start_chainage float,
                end_chainage float,
                offset float default 0 not null
             )
        '''
   
    runQuery(q)
    
    
    q = '''create table if not exists corrections
            ( 
                 pk INTEGER PRIMARY KEY,
                 run text,
                 start_chainage float,
                 start_offset float,
                 end_chainage float,
                 end_offset float
             )
        '''
   
    runQuery(q)
    db.commit()
    
    
import csv
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject,QgsPoint


def loadGps(file,db):
    
    
    db.transaction()
    r = db.exec('delete from gps')
    if not r:
        raise queryError(r)


  #  transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),
   #     QgsCoordinateReferenceSystem('EPSG:27700'),
   #     QgsProject.instance())    
    
    q = QSqlQuery(db)
    #if not q.prepare('insert into gps(m,x,y) values(:m,:x,:y)'):
    if not q.prepare('insert into gps(m,pt) values(:m,ST_Transform(MakePointM(:lon,:lat,:m,4326),27700))'):
        raise queryError(q)
    
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        
        for i,d in enumerate(reader):
            lon = float(d['Longitude (deg)'])
            lat = float(d['Latitude (deg)'])
         #   pt = transform.transform(x,y)
            m = float(d['Chainage (km)'])*1000
            q.bindValue(':m',m)
            q.bindValue(':lat',lat)
            q.bindValue(':lon',lon)

            if not q.exec():
                print(q.boundValues())
                raise queryError(q)
                
    #set last here. file might not necessarily be ordered...
    runQuery('update gps set last_m = (select m from gps as a where a.m < gps.m order by m desc limit 1)')
    runQuery('update gps set next_m = (select m from gps as a where a.m > gps.m order by m asc limit 1)')

   # print(a[990:1010])
    #print(values[990:1010])
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





#mock up. doesnt use corrections yet.
#numpy.interp(x, xp, fp, left=None, right=None, period=None)
def recalcChainages(pks=None):
    db = QSqlDatabase.database('image_loader')
    db.transaction()


    runQuery(query = 'update images set start_chainage = image_id*5,end_chainage = image_id*5 +5')
    db.commit()

    



from qgis.core import QgsGeometry


#->QgsGeometry LineStringM
def getLine(db,start,end):
    t = 'select m,st_x(pt) as x,st_y(pt) as y from gps where last <= :end and next >= :start order by m'
    
    q = QSqlQuery(db)

    if not q.prepare(t):
        raise queryError(q)

    q.bindValue(':start',start)
    q.bindValue(':end',end)

    if not q.exec():
        print(q.boundValues())
        raise queryError(q)
    
    
    points = []
    
    while q.next():
        #print(query.value(0),query.value(1),query.value(2))
        points.append(QgsPoint( m = q.value(0), x = q.value(1),y = q.value(2) ))
    
 #   print('points',points)
    
    if len(points)<2:#need at least 2 points for line.
        return


    r = []
    last = QgsPoint()
    #points ordered by m
    for point in points:
        #interpolate start
        if last.m()<start and start<point.m():
            v = interpolate(start = toVector(last),
                            startM = last.m(),
                            end = toVector(point),
                            endM = point.m(),
                            m = start)
            
            r.append(QgsPoint(x=v[0] ,y=v[1] , m=start))
          
        if start<=point.m() and point.m()<=end:
            r.append(point)
         
        #interpolate end
         
        if last.m()<end and end<point.m():
            v = interpolate(start = toVector(last),
                            startM = last.m(),
                            end = toVector(point),
                            endM = point.m(),
                            m = end)
            
            r.append(QgsPoint(x=v[0] ,y=v[1] , m=end))
         
        last = point
            
    return QgsGeometry.fromPolyline(r)
            


def unused_getLine(db,start,end):
    
    q = QSqlQuery(db)

    #join points into linestringm. use ST_Line_Substring to get parts between measures.
    #ST_Locate_Between_Measures does not interpolate ends.
    #ST_Line_Substring sets m to 0 on old spatialite versions.
    #called ST_LineSubstring on newer versions.
    
    t = '''select ST_AsText(st_addMeasure(ST_Line_Substring(MakeLine(pt),(10.2-min(m))/(max(m)-min(m)),(20.5-min(m))/(max(m)-min(m))),:start,:end)) 
        from gps where last <= :end and next >= :start order by m
        '''
    
    if not q.prepare(t):
        raise queryError(q)

    q.bindValue(':start',start)
    q.bindValue(':end',end)

    if not q.exec():
        print(q.boundValues())
        raise queryError(q)
        
        
    while q.next():
        return q.value(0)
        
        

def createDb():    
    db = QSqlDatabase.addDatabase("QSPATIALITE",'image_loader')
    dbFile = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\images.db'
   # dbFile = ':memory:'
    
    db.setDatabaseName(dbFile)
    if not db.open():
        raise ValueError('could not open database')
        
    initDb(db)
    return db



import os

def test():
    try:
        db = createDb()

        folder = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007'
        file = os.path.join(folder,'MFV1_007-rutacd-1.csv')

        loadGps(db=db,file=file)

        #line = getLine(db,10,20)
        
        line = getLine(db,20.5,30.2)

        print('line',line)
        
    except Exception as e  :
        print(e)
        
        
    finally:
        db.close()
    
    
if __name__ =='__console__':
    test()
