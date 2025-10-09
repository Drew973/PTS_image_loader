# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 08:57:51 2025

@author: Drew.Bennett


functions for communicating with database
start moving everything database specific to here.

make as procedural as possible for easier testing. unavoidable dependency on database state but not on state of some model



"""

from image_loader.db_functions import runQuery, defaultDb, queryError , prepareQuery
import numpy as np
from qgis.core import QgsGeometry
from image_loader import settings , db_functions , dims
from image_loader.backend import runs_functions , splinestring , anpp

import csv
import math
from image_loader.type_conversions import asBool,asInt,asFloat

import os
from image_loader.backend.splinestring import splineString , mxyType

from qgis.core import QgsPointXY , QgsCoordinateTransform , QgsCoordinateReferenceSystem , QgsProject




class MO:
    def __init__(self , m:float , offset:float):
        self.m = float(m)
        self.offset = float(offset)
    def __repr__(self):
        return 'MOPoint({m},{offset})'.format(m=self.m,offset = self.offset)
        


def uploadAnpp(fileName:str) -> None:
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
    
    s = splineString(mxy.view(dtype = mxyType))
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





#ESPG:4326
#meant for rutacd csvs. 1m intervals
def parseCsv(file : str , interval:float = 5):
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



def uploadFile(filePath) -> None:
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



def clearGps():
    runQuery(query='delete from original_points')



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


recalcSpline() 
    
#array [(m1,offset1),(m2,offset2)...]
#array [(x1,y1),(x2,y2)...]
def getGpsPoint(m:float , offset:float) -> QgsPointXY:
    if spline is not None:
        p = spline.point(m,offset)#array[[x,y]]
        return QgsPointXY(p[0],p[1])
    return QgsPointXY()



def MOToXY(values:list[MO]) -> list[QgsPointXY]:
    if len(values) > 0 and spline is not None:
        mo = np.array([(p.m,p.offset) for p in values])
        return [QgsPointXY(r[0],r[1]) for r in spline.points(mo)]#array[[x,y]]
    return []


#find m,offset for x,y with minM<=m<=maxM
def mo(x:float , y:float , minM:float = 0.0 , maxM:float|None = None , tol:float|None = 0.01) -> tuple[float,float]:
    if spline is not None:
        return spline.locate(x , y , minM , maxM , tol)

    return (0.0 , 0.0)


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
    return 0
    



#in QSettings srid
#start,multiples of interval,end
def centerLine(startM:float , endM:float , interval = dims.HEIGHT) -> list[QgsPointXY] :
    if spline is not None:
        s:float = min([startM,endM])
        e:float = max([startM,endM])
        a:int = math.ceil(s/interval) * interval        
        b:int =  math.ceil(e/interval) * interval        
       # m:np.ndarray = np.unique(np.concatenate(([s],np.arange(a,b,interval),[e])))#float array
       
        mVals = [s] + [v for v in range(a,b,interval)] + [e]
        m = np.array(mVals,dtype = float)
        
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
    
    
    
    
    




#only used for testing
def allImagePks():
    pks = []
    query = runQuery('select pk from images order by pk')
    while query.next():
        pks.append(query.value(0))
    return pks




#only used for testing
def allRunPks():
    q = runQuery('select pk from runs order by pk')
    pks = []
    while q.next():
        pks.append(q.value(0))        
    return pks


def clearImages():
    runQuery('delete from images')



#start_frame,end_frame
def frameRange(runPk:int):
    q = runQuery('select start_frame,end_frame from runs where pk = :pk',values = {':pk':runPk})
    while q.next():
        return (q.value(0),q.value(1))
    return (0,int(dims.MAX))
    
    






def saveCorrectionsCsv(filePath:str):
    with open(filePath , 'w' , newline='') as f:
        writer = csv.writer(f)
        fields = ['frame','line','pixel','new_chainage','new_offset','lon','lat']
        writer.writerow(fields)
        q = db_functions.runQuery('select frame,line,pixel,new_chainage,new_offset,lon,lat from corrections')
        while q.next():
            writer.writerow([q.value(i) for i,f in enumerate(fields)])

    


def loadCorrectionsCsv(filePath:str):
    db = db_functions.defaultDb()
    db.transaction()
    
    try:
        fields = [':frame',':line',':pixel',':new_chainage',':new_offset',':lon',':lat']
        qs = 'insert into corrections(frame,line,pixel,new_chainage,new_offset,lon,lat) values(:frame,:line,:pixel,:new_chainage,:new_offset,:lon,:lat)'
        insertQuery = db_functions.prepareQuery(qs , db = db)
        with open(filePath , 'r' , newline='') as f:
            reader = csv.reader(f , dialect='excel' , delimiter = ',')
            for r in reader:
                for i,field in enumerate(fields):
                    insertQuery.bindValue(field,r[i])
                if not insertQuery.exec():
                    raise db_functions.queryError(insertQuery)
                    
        db_functions.runQuery('update corrections set run = (select pk from runs where start_frame<= frame and end_frame >= frame limit 1)' , db = db)

        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e






#only using to update rows added with versions before corrections_model set x and x.
def updateXY():
    try:
        db = db_functions.defaultDb()
        db.transaction()
        updateQuery = db_functions.prepareQuery('update corrections set lat = :lat , lon = :lon where pk = :pk')
        
        
        t = settings.transformFromDestCrs(4326)
        
        q = db_functions.runQuery('select pk,new_chainage,new_offset from corrections where lat is null or lon is null' , db = db)
        while q.next():
            p = getGpsPoint(m = q.value(1) , offset = q.value(2))
            
            pt = t.transform(p)
            updateQuery.bindValue(':lon',pt.x())
            updateQuery.bindValue(':lat',pt.y())
            updateQuery.bindValue(':pk',q.value(0))
            if not updateQuery.exec():
                raise db_functions.queryError(updateQuery)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    
    

def insertCorrection(frame:int , line:int , pixel:int , m:float , offset:float ,lon:float , lat:float , run:int):
    
    
    db_functions.runQuery('insert into corrections(frame,line,pixel,new_chainage,new_offset,lon,lat,run) values (:frame,:line,:pixel,:m,:offset,:lon,:lat,:run)',
                          values = {':frame':frame , ':line':line , ':pixel':pixel , ':m':m,':offset':offset , ':lon':lon , ':lat':lat , ':run':run})



def dropCorrections(pks:list[int]):
    q = db_functions.prepareQuery('delete from corrections where pk = :pk')
    for pk in pks:
        q.bindValue(':pk',pk)
        if not q.exec():
            raise db_functions.queryError(q)




def clearCorrections():
    db_functions.runQuery('delete from corrections')
    
    

def loadCsv(filePath : str):
    pass



def saveCsv(filePath : str):
    pass




#wrong
#geometry for corrections dialog
def getCorrectionGeom(frame:int , pixel : int , line:int , chainage:float , offset:float) -> QgsGeometry:
    startM = dims.lineToM(frame = frame, line = line)
    startOffset = dims.pixelToOffset(pixel)    
    runPk = runs_functions.runFromFrame(frame)
    s:splinestring.splineString | None = _getCorrectedSpline(runPk = runPk)
    #if hasattr(s,'point'):
    if isinstance(s , splinestring.splineString):

        sp = s.point(m = startM , offset = startOffset)
        points = [QgsPointXY(sp[0],sp[1])] + [getGpsPoint(chainage,offset)]
        return QgsGeometry.fromPolylineXY(points)
    return QgsGeometry()



#array [(m1,x1,y1)...]
#splineString from projected points stored in database. In whatever srid last set.
def _getCorrectedSpline(runPk:int) -> splinestring.splineString | None:
    q = db_functions.runQuery('select m,x,y from corrected_points where run = :run and x is not null and y is not null order by m',
                                values = {':run':runPk},
                                forwardOnly = True)
    mxy = []
    while q.next():
        mxy.append( [ float(q.value(0)) , float(q.value(1)) , float(q.value(2)) ] )
        
        
    tempmxy = np.array(mxy,dtype = float)
    
    
    mxya = tempmxy.view(splinestring.mxyType)
        
    if len(mxya) > splinestring.K:
        return splinestring.splineString(values = mxya)
    
    return None
    
    
    
    
    
#-> '-gcp <pixel> <line> <easting> <northing>'
#might as well serialize to string here. list is valid JSON and avoids passing "" to CLI
N = 2 # GCP points per side of frame
def calcGcps(frame : int , geom : splinestring.splineString) -> str:
     startM = dims.frameToM(frame)
     endM = startM + dims.HEIGHT
     mo = np.zeros((N*2,2)) * np.nan
     mo[:,0][0:N] = np.linspace(startM,endM,N)
     mo[:,0][N:] = np.linspace(startM,endM,N)
     mo[:,1][0:N] = dims.WIDTH/2
     mo[:,1][N:] = - dims.WIDTH/2
     xy = geom.points(mo)
     r = np.zeros((N*2,4)) * np.nan
     r[:,0:2] = xy
     r[:,2][0:N] = 0
     r[:,2][N:] = dims.PIXELS
     r[:,3][0:N] = np.linspace(dims.LINES,0,N)
     r[:,3][N:] = np.linspace(dims.LINES,0,N)
     #v = [(row[0],row[1],int(row[2]),int(row[3])) for row in r]
     #-gcp <pixel> <line> <easting> <northing> [<elevation>]
     return ' '.join(['-gcp {pixel} {line} {easting} {northing}'.format(pixel = int(a[2] ), line = int(a[3]) , easting = a[0] , northing = a[1]) for a in r])
     


#uses corrected_points 
def XYToFramePixelLine(x:float , y:float , runPk:int) -> tuple[int , int , int]:
    
    #print('runPk',runPk,'x',x,'y',y)
    s = _getCorrectedSpline(runPk)
    
    #use original_points where no corrections yet
    if s is None:
        m,offset = locate(x = x , y = y , runPk = runPk)
        
    if s is not None:        
        m,offset = s.locate(x = x , y = y)
    
   # print('s',s,'m:',m,'offset:',offset)
        
    frame = dims.mToFrame(m)
    line = dims.mToLine(m = m , frame = frame)
    pixel = dims.offsetToPixel(offset)
    return (frame , pixel , line)

    return (-1,-1,-1)



#uses corrected_points 
def framePixelLineToXY(frame:int , pixel:int , line:int , runPk:int) -> QgsPointXY:
    s = _getCorrectedSpline(runPk)
    m = dims.lineToM(line = line,frame = frame)
    offset = dims.pixelToOffset(pixel)
    #use original_points where no corrections yet
    if s is None:
        return getGpsPoint(m = m , offset = offset)        
    else:        
        p = s.point(m = m , offset = offset)
        return QgsPointXY(p[0],p[1])        
    #return QgsPointXY()




#update table. only need frames within runs in corrected_points.
def correctRun(runPk:int , db = None) -> None:
    if db is None:
        db = db_functions.defaultDb()
        
    db.transaction()
    
    

    db_functions.runQuery('delete from corrected_points where run = :run' , 
                          values = {':run':runPk} ,
                          db = db)
    
    
    mVals = [f * dims.HEIGHT for f in runs_functions.frames(runPk)]
    points = [MO(m,0) for m in mVals]
    insertQuery = db_functions.prepareQuery('insert into corrected_points(m,x,y,run) values (:m,:x,:y,:run)' , db = db)

    cp = correctMO(values = points , runPk = runPk)
    correctedPoints:list[QgsPointXY] = MOToXY(cp)

    for i,p in enumerate(correctedPoints):
        insertQuery.bindValue(':m',mVals[i])
        insertQuery.bindValue(':x',p.x())
        insertQuery.bindValue(':y',p.y())
        insertQuery.bindValue(':run',runPk)
        if not insertQuery.exec():
            raise db_functions.queryError(insertQuery)

    #print(correctedPoints)
    db.commit()
    return


#############freezes?
def correctMO(values:list[MO] , runPk:int) -> list[MO]:
    print('values',values)
    q = db_functions.runQuery('select frame,line,pixel,new_chainage,new_offset from corrections where run = :run order by frame , line desc', values = {':run':runPk})   

    mValues = []
    mCorrections = []
    offsetCorrections = []
    
    while q.next():
        mv = dims.lineToM(frame = q.value(0), line = q.value(1))
        mValues.append(mv)
        mCorrections.append(q.value(3) - mv)
        offsetCorrections.append(q.value(4) - dims.pixelToOffset(q.value(2)))


    #values unchanged if no corrections for run
    if len(mValues) == 0:
        return values
        

    #np.interp returns left or right for values outside xp
    if len(mValues) > 0:
        m = [p.m for p in values]
        
        correctedChainages = [p.m for p in values] + np.interp(x = m , 
                  xp = mValues , 
                  fp = mCorrections)
    
        correctedOffsets = [p.offset for p in values] + np.interp(x = m , 
                  xp = mValues , 
                  fp = offsetCorrections)
            
        r = []
        for i,ch in enumerate(correctedChainages):
            r.append(MO(ch,correctedOffsets[i]))
            
        print('r:\n',r)
        return r
    return []
