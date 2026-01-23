# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 11:59:35 2024

@author: Drew.Bennett

make as procedural as possible for easier testing. database state for testing?

"""


import numpy as np
import csv
import math
from image_loader import settings,dims
from image_loader.db_functions import runQuery, defaultDb, queryError , prepareQuery
from image_loader.type_conversions import asBool,asInt,asFloat


import os
from image_loader.backend import anpp,runs_functions
from image_loader.splinestring import splineString , mxyType


from qgis.core import QgsPointXY , QgsCoordinateTransform , QgsCoordinateReferenceSystem , QgsProject



class MO:
    def __init__(self , m:float , offset:float):
        self.m = float(m)
        self.offset = float(offset)
    def __repr__(self):
        return 'MOPoint({m},{offset})'.format(m=self.m,offset = self.offset)
        


def uploadAnpp(fileName):
    srid = asInt(settings.value('destSrid'),27700)
    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326) , QgsCoordinateReferenceSystem(srid) , QgsProject.instance())
    dt = np.dtype([('x',float),('y',float),('seconds',int),('microSeconds',int)])
    
    def toDt(r):
        p = transform.transform(QgsPointXY(r.lat,r.lon))
        return (p.x() , p.y() , r.seconds , r.microSeconds)
    
    data = np.sort(np.array([toDt(r) for r in anpp.readAnpp(fileName)] , dtype = dt),order = ['seconds','microSeconds'])
    m = np.cumsum(np.sqrt(np.diff(data['x'])*np.diff(data['x']) + np.diff(data['y'])*np.diff(data['y'])) , dtype = float)
    #print(data)
    #print('m',m)
    m = np.insert(m , 0 , 0.0)#add 0.0 to start.
    
    mxy = np.column_stack((m, data['x'] , data['y']))
    mxy.dtype = mxyType
    
    s = splineString(mxy)
    print('mxy',mxy)
    _uploadSplineString(s)
    #print(s)
    return




def _uploadSplineString(spline:splineString , interval:float = 5.0):
    
    db = defaultDb()
    db.transaction()
    runQuery('delete from original_points' , db = db)
    mVals = np.arange(start = spline.minM , stop = spline.maxM , step = interval)
    
    points = spline.centerLinePoint(mVals)
   # print('points',points)
    
    q = prepareQuery('insert into original_points (m,x,y) values (:m , :x , :y)' , db = db)

    for i,m in enumerate(mVals):
        q.bindValue(':m' , float(m))
        q.bindValue(':x' , float(points[i,0]))
        q.bindValue(':y' , float(points[i,1]))
        if not q.exec():
            raise queryError(q)


    #apply start at 0 setting
    if asBool(settings.value('startAtZero'),True):
        runQuery('update original_points set m = m - (select min(m) from original_points)', db=db)
        
    #update original_points next_id,last_id
    runQuery('update original_points set next_id = (select id from original_points as np where np.m>original_points.m order by np.m limit 1)', db=db)
    runQuery('update original_points set last_id = (select id from original_points as np where np.m<original_points.m order by np.m desc limit 1)', db=db)
    runQuery('update original_points set bearing = (select next_point.bearing from next_point where next_point.id = original_points.id)')
    
    runQuery('update original_points set lon = st_x(ST_Transform(MakePoint(x,y,:srid),4326)) , lat = st_y(ST_Transform(MakePoint(x,y,:srid),4326))',values = {':srid':settings.destSrid()})

    db.commit()




def depreciatedUploadAnpp(fileName):
    srid = asInt(settings.value('destSrid'),27700)

    db = defaultDb()
    db.transaction()
    runQuery('delete from original_points' , db = db)
    
    q = prepareQuery('insert or ignore into original_points (lon,lat,alt,seconds,milliseconds) values (:lon,:lat,:alt,:seconds,:milliseconds)',db = db)
    
    for r in anpp.readAnpp(fileName):
        q.bindValue(':lon',r.lon)
        q.bindValue(':lat',r.lat)
        q.bindValue(':alt',r.alt)
        q.bindValue(':seconds',r.seconds)
        q.bindValue(':milliseconds',int(r.microSeconds/1000))
        if not q.exec():
            raise queryError(q)
            
     
    
    runQuery('update original_points set x = st_x(ST_Transform(MakePoint(lon,lat,4326),:srid)) , y = st_y(ST_Transform(MakePoint(lon,lat,4326),:srid))',values = {':srid':srid} , db=db)
            
    qs = '''
    update original_points set m = points_update_2.m
    ,bearing = points_update_2.bearing 
    ,next_id = points_update_2.next_id
    ,last_id = points_update_2.last_id
    from points_update_2 where points_update_2.id = original_points.id
    '''
    runQuery(qs , db = db)
         
    runQuery('delete from original_points where m in (select m from original_points group by m having count(m)>1)',db=db)#remove duplicate points
            
    db.commit()




#ESPG:4326
#meant for rutacd csvs. 1m intervals
def parseCsv(file : str , interval = 5):
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for i , d in enumerate(reader):
            try:
                # need round to avoid floating point errors like int(1.001*1000) = 1000
                m : int = round(float(d['Chainage (km)'])*1000)
                lon = float(d['Longitude (deg)'])
                lat = float(d['Latitude (deg)'])
                alt = float(d['Altitude (m)'])
                yield ( m , lon , lat , alt )
            except Exception as e:
                print(e)
                pass



def uploadCsv(filePath):
    srid = asInt(settings.value('destSrid'),27700)

    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326) , QgsCoordinateReferenceSystem(srid) , QgsProject.instance())

    mxy = []
       
    for i,r in enumerate(parseCsv(filePath)):
        #print(r)
     
        try:
            p = transform.transform(QgsPointXY(float(r[1]),float(r[2])))
            mxy.append((float(r[0]),p.x(),p.y()))
        except:
            pass


    mxy = np.array(mxy)
    mxy.dtype = mxyType
    
    print('mxy',mxy)

    s = splineString(mxy)
    _uploadSplineString(s)



def uploadFile(filePath:str,mfv:str) -> None:
    ext = os.path.splitext(filePath)[1]
    
    if ext == '.csv':
        uploadCsv(filePath)
    
    if ext == '.anpp':
        uploadAnpp(filePath)

    recalcSpline()
    updateFrames()


#generator of int
def frameNumbers():
    m = math.ceil(maxM()/dims.HEIGHT)
    for frame in range(0,m):
        yield frame


def updateFrames():
    db = defaultDb()
    db.transaction()
    runQuery('delete from frames' , db=db)
    q = prepareQuery('insert into frames(id) values (:f)' , db=db)
    for frame in frameNumbers():
        q.bindValue(':f',frame)
        q.exec()
    db.commit()
    
    

def clearGps():
    runQuery('delete from original_points')


#sets x,y,bearing
def reproject():
    srid = asInt(settings.value('destSrid'),27700)
    #print('reprojecting to :'+str(srid))
   # runQuery('update original_points set x = st_x(ST_Transform(MakePoint(lon,lat,4326),:srid)) , y = st_y(ST_Transform(MakePoint(lon,lat,4326),:srid))',values = {':srid':srid})
   # runQuery('update original_points set bearing = (select next_point.bearing from next_point where next_point.id = original_points.id)')
    
    

def maxM() -> float:
    q = runQuery('select max(m) from original_points')
    while q.next():
        v =  q.value(0)
        if isinstance(v,float):
            return v
        return 0.0
    
    
 
def minM() -> int:
    q = runQuery('select min(m) from original_points')
    while q.next():
        return q.value(0)
    return 0



def pointCount() -> int:
    q = runQuery('select count(m) from original_points')
    while q.next():
        return q.value(0)
    return 0




#array [(m1,x1,y1)...]    
#spatialite reprojection ~1.5m from QGIS reprojection
#reproject in QGIS?
#~0.15s
#splineString from projected points stored in database. In whatever srid last set.

#-> splineString or None
def getSplineString():
    q = runQuery('select m , x , y from original_points where m is not null and x is not null and y is not null order by m',
                 forwardOnly = True)
    mxy = []
    while q.next():
        mxy.append( [ float(q.value(0)) , float(q.value(1)) , float(q.value(2)) ] )
        
    
    mxy = np.array(mxy)
    mxy.dtype = mxyType
        
    if len(mxy) > 0:
        return splineString(values = np.array(mxy))
  
    
    
spline = None
def recalcSpline():
    global spline 
    spline = getSplineString()


    
#array [(m1,offset1),(m2,offset2)...]
#array [(x1,y1),(x2,y2)...]
def point(m:float , offset:float) -> QgsPointXY:
    if spline is not None:
        p = spline.point(m,offset)#array[[x,y]]
        return QgsPointXY(p[0],p[1])
    return QgsPointXY()



def MOToXY(values:list[MO]) -> list[QgsPointXY]:
    if len(values) > 0 and spline is not None:
        mo = np.array([(p.m,p.offset) for p in values])
        return [QgsPointXY(r[0],r[1]) for r in spline.points(mo)]#array[[x,y]]
    return []



def mo(x:float , y:float , minM:float = 0.0 , maxM:float = None , tol:float = 0.01) -> tuple:
    if spline is not None:
        return spline.locate(x , y , minM , maxM , tol)



def locate(x:float , y:float , runPk:int):
    if spline is not None:
        mr = runs_functions.mRange(runPk)
        if mr is not None:
            outsideRunDistance = asFloat(settings.value('outsideRunDistance') , 50.0)
            minM = mr[0] - outsideRunDistance
            maxM = mr[1] + outsideRunDistance
            return spline.locate(x , y , minM , maxM)


#only used by chainages dialog. speed unimportant.
#start of frame. point in wgs84 / EPSG:4326
#point in destCrs
def pointToFrame(point , maxDist : float = 10.0) -> int:
    if spline is not None:
        mVals = np.arange(0 , maxM() , dims.HEIGHT/4)
        xy = spline.centerLinePoint(mVals)
        sqdif = (xy[:,0] - point.x())*(xy[:,0] - point.x()) + (xy[:,1] - point.y())*(xy[:,1] - point.y())
        return dims.mToFrame(mVals[np.argmin(sqdif)])

    



#in QSettings srid
#start,multiples of interval,end
def centerLine(startM:float , endM:float , interval = dims.HEIGHT) -> list[QgsPointXY] :
    if spline is not None:
        s:float = min([startM,endM])
        e:float = max([startM,endM])
        a:int = math.ceil(s/interval) * interval        
        b:int =  math.ceil(e/interval) * interval        
        m = np.unique(np.concatenate(([s],np.arange(a,b,interval),[e])))
        #print(m)
        if len(m) > 0:
            points = [QgsPointXY(r[0],r[1]) for r in spline.centerLinePoint(m)]
            if startM < endM:
                return points
            if startM > endM:
                points.reverse()
                return points
    return []
        
    
K = 2
S = 0   
from scipy import interpolate
  
    
#unused WIP
#finding and uploading coefficients
def _updateSpline():
    q = runQuery('select m , x , y from original_points order by m',
                 forwardOnly = True)
    m = []
    x = []
    y = []
    while q.next():
        try:
            m.append(float(q.value(0)))
            x.append(float(q.value(1)))
            y.append(float(q.value(2)))
        except Exception as e:
            pass
        

    xPoly = interpolate.PPoly.from_spline(interpolate.splrep(m , x , k = K , s = S))
    yPoly = interpolate.PPoly.from_spline(interpolate.splrep(m , y , k = K , s = S))
    print(xPoly.c)
    xPoly.c[0]
    
    
    for i in range(0,xPoly.c.shape[1]):
        #x = x0 + x1*m + x2*m*m 
        
        x2 = xPoly.c[K-2,i]
        x1 = xPoly.c[K-1,i]
        x0 = xPoly.c[K,i]

        y2 = yPoly.c[K-2,i]
        y1 = yPoly.c[K-1,i]
        y0 = yPoly.c[K,i]


    print(x0,x1,x2)
    
    
    
    
    
    
    
    
    

if __name__ == '__console__':
#    recalcSpline()
    getSplineString(runPk = 1)




