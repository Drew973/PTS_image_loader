# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 11:44:13 2023

@author: Drew.Bennett


need:
frame,pixel,line <-> corrected x,y for corrections.
chainage limits for chainage dialogs.
originalLine for displaying chainage ranges.

apply_corrections() to update corrected_points table

updateGCP() to update gcp table.

"""

from image_loader.splinestring import splineStringM,points
from image_loader.db_functions import defaultDb,runQuery,queryError,queryPrepareError
from image_loader import geometry_functions

from qgis.core import QgsPointXY,QgsGeometry,QgsPoint
from PyQt5.QtSql import QSqlQuery
import csv
import numpy
import os

from image_loader.load_center_shapefile import loadShapefile

WIDTH = 4.0
PIXELS = 1038
LINES = 1250
HEIGHT = 5.0

#todo:
#PRAGMA synchronous = OFF
#PRAGMA journal_mode = MEMORY
#ignore duplicate rows after 1st and where wrong type


def asFloat(v,default=None):
    try:
        return float(v)
    except:
        return default


def loadCsv(file,db=None):
    if db is None:
        db = defaultDb()
    db.transaction()
    runQuery(db=db,query='delete from original_points')
    q = QSqlQuery(db)
    if not q.prepare('insert into original_points(m,pt) values(:m,st_transform(MakePoint(:x,:y,4326),27700))'):
        raise queryError(q)
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        for i,d in enumerate(reader):
            try:
                m = round(float(d['Chainage (km)'])*1000)# need round to avoid floating point errors like int(1.001*1000) = 1000
                x = float(d['Longitude (deg)'])
                y = float(d['Latitude (deg)'])
                q.bindValue(':m',m)
                q.bindValue(':x',x)
                q.bindValue(':y',y)
                if not q.exec():
                    raise queryError(q)
            except Exception as e:
                message = 'error loading row {r} : {err}'.format(r = i,err = e)
                print(message)
    runQuery(db=db,query='update original_points set next_id = (select id from original_points as np where np.m>original_points.m order by np.m limit 1)')
    runQuery(db=db,query='delete from corrected_points')
    runQuery(db=db,query='insert into corrected_points(m,pt) select m,pt from original_points')
    db.commit()



def _line(m,frame):
    startM = (frame-1)*HEIGHT
    endM = frame*HEIGHT
    if m<startM:
        return LINES
    if m>endM:
        return 0
    return round(LINES - LINES*(m-startM)/HEIGHT)
  

def _offsetToPixel(offset):
    return round(PIXELS * 0.5 - offset * PIXELS / WIDTH )


def _pixelToOffset(pixel):
    return WIDTH*0.5-pixel*WIDTH/PIXELS


#pixel =0: offset = WIDTH/2
#pixel = PIXELS/2 offset = 0



class gpsModel:
    
    def __init__(self):
        self.run = None
        self._downloadGeom()

    def hasGps(self):
        return self.geom is not None
    
    
    @staticmethod
    def lineToM(frame,line):
        return HEIGHT * (frame-line/LINES)
        
    
    def loadFile(self,file):
        ext = os.path.splitext(file)[1]
       # print('loading gps ',ext)
        
        if ext == '.csv':
            loadCsv(file)
            self._downloadGeom()
        
        if ext == '.shp':
            loadShapefile(file)
            self._downloadGeom()
            #self.rechainage()
    
    
    def clear(self):
        runQuery('delete from corrected_points')
        runQuery('delete from original_points')
        self._downloadGeom()
        
    #uncorrected
    #tuple. chainage,left_offset
    def getPoint(self,frameId,pixel,line):
        if self.geom is not None:
            m = self.lineToM(frame=frameId,line=line)
            offset = _pixelToOffset(pixel)
            try:
                xy = self.geom.interpolatePoints([m],[offset])
                return QgsPointXY(xy[0],xy[1])
            except Exception as e:
                print(e)
                return QgsPointXY()
    
    
    
    def currentPointFromM(self,m,offset):
        xy = self.geom.interpolatePoints([m],[offset])
        return QgsPointXY(xy[0],xy[1])
    
    
    def originalPointFromM(self,m,offset):
        if self.originalGeom is not None:
            xy = self.originalGeom.interpolatePoints([m],[offset])
            return QgsPointXY(xy[0],xy[1])
        
        
    @staticmethod                
    def originalPoint(m,offset):
        q = 'select Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)) from corrected_lines where start_m<=:m and end_m <= :m'
        query = runQuery(query = q , values = {':m':m})
        while query.next():
            return q.value(1)
    
    
    @staticmethod        
    def getFrame(point,minM=0,maxM=99999999999999999999999):
        m = gpsModel.closestCorrectedM(point,minM,maxM)
        if m is not None:
            return numpy.floor(m/HEIGHT)+1
        
    @staticmethod        
    def closestCorrectedM(point,minM=0,maxM=99999999999999999999999):
        mQuery = '''select st_z(st_closestPoint(line,makePoint(:x,:y,27700)))
        from corrected_lines where end_m >= :s and start_m <= :e 
        order by ST_Distance(line,makePoint(:x,:y,27700)) limit 1'''
        q = runQuery(mQuery,values = {':x':point.x(),':y':point.y(),':s':minM,':e':maxM})
        while q.next():
           return asFloat(q.value(0))


    #(chainage,offset)
    #direction for offset left perpedicular to line joining closest m -+HEIGHT/2
    @staticmethod                
    def originalChainage(point,minM=0,maxM=99999999999999999999999):
        m = gpsModel.closestOriginalM(point,minM,maxM)
        line = gpsModel.originalLine(m-HEIGHT/2,m+HEIGHT/2)
        forward = geometry_functions.asVector(line)
        perp = geometry_functions.unitVector(geometry_functions.leftPerp(forward))
        shortest = geometry_functions.asVector(line.shortestLine(QgsGeometry.fromPointXY(point)))
        offset = numpy.dot(shortest,perp)
        return (m,offset)


  #  @staticmethod                
  #  def pixelLine(self,frameId,point):
   #     m,off = gpsModel.originalChainage(point)
        
        
    #-> float
    @staticmethod        
    def closestOriginalM(point,minM=0,maxM=99999999999999999999999):
        mQuery = '''select st_z(st_closestPoint(line,makePoint(:x,:y,27700)) )
        from lines where end_m >= :s and start_m <= :e 
        order by ST_Distance(line,makePoint(:x,:y,27700)) limit 1'''
        q = runQuery(mQuery,values = {':x':point.x(),':y':point.y(),':s':minM,':e':maxM})
        while q.next():
           return asFloat(q.value(0))
    
    
    #corrected position
    def getOriginalChainage(self,point):
        if self.originalGeom is not None:
            mQuery = '''
            select start_m+(end_m-start_m)*Line_Locate_Point(line,makePoint(:x,:y,27700)) 
            from lines order by ST_Distance(line,makePoint(:x,:y,27700)) limit 1
            '''
            q = runQuery(mQuery,values = {':x':point.x(),':y':point.y()})
            while q.next():
                m = asFloat(q.value(0))
                if m is not None:
                    #print('m',m)
                    nearest = self.originalGeom.interpolatePoints([m])
                    #print('nearest',nearest)
                    shortest = numpy.array([point.x()-nearest[0,0],point.y()-nearest[1,0]])#nearestPoint on centerline -> point
                    perps = self.originalGeom.leftPerps([m])
                    perp = numpy.array([perps[0,0],perps[1,0]])#row,col
                    offset = numpy.dot(shortest,perp)
                #    print(offset)
                    return (m,offset)
        else:
            print('No geometry. Is gps data loaded?')
            
            
    #corrected position
    def getPixelLine(self,frameId,point):
        if self.geom is not None:
            mQuery = '''
            select start_m+(end_m-start_m)*Line_Locate_Point(line,makePoint(:x,:y,27700)) 
            from corrected_lines where start_m <= :e and end_m>= :s order by ST_Distance(line,makePoint(:x,:y,27700)) limit 1
            '''
            q = runQuery(mQuery,values = {':frame':frameId,':x':point.x(),':y':point.y(),':s':frameId*5-5,':e':frameId*5})
            while q.next():
                m = asFloat(q.value(0))
                if m is not None:
                    #print('m',m)
                    nearest = self.geom.interpolatePoints([m])
                    #print('nearest',nearest)
                    shortest = numpy.array([point.x()-nearest[0,0],point.y()-nearest[1,0]])#nearestPoint on centerline -> point
                    perps = self.geom.leftPerps([m])
                    perp = numpy.array([perps[0,0],perps[1,0]])#row,col
                    offset = numpy.dot(shortest,perp)
                #    print(offset)
                    return (_offsetToPixel(offset),_line(m=m,frame=frameId))
        else:
            print('No geometry. Is gps data loaded?')
            
            
    def setRun(self,run):
        #print('setRun',run)
        self.run = run
    
    
    
    
    @staticmethod
    def applyChainageCorrections():
        db = defaultDb()
        db.transaction()
        
        runQuery(query = 'delete from corrected_points',db = db)
        
        #-- left perp of x,y is -y,x
        insertQuery = '''
insert into corrected_points(id,next_id,m,pt)

select id
,next_id
,m-chainage_correction
,makePoint(st_x(pt) + left_offset*perp_x/sqrt(perp_x*perp_x + perp_y*perp_y)
	,st_y(pt) + left_offset*perp_y/sqrt(perp_x*perp_x + perp_y*perp_y),
	27700)

from
(select id,next_id,m,pt,chainage_correction,left_offset


,(select st_x(Line_Interpolate_Point(line,(m+2.5+start_m)/(end_m-start_m)))
        from lines where start_m <= m+2.5 and end_m >= m+2.5
)
-
(select st_x(Line_Interpolate_Point(line,(m-2.5-start_m)/(end_m-start_m)))
        from lines where start_m <= m-2.5 and end_m >= m-2.5
) as perp_y

,(select st_y(Line_Interpolate_Point(line,(m-2.5-start_m)/(end_m-start_m)))
        from lines where start_m <= m-2.5 and end_m >= m-2.5
)
-
(select st_y(Line_Interpolate_Point(line,(m+2.5+start_m)/(end_m-start_m)))
    from lines where start_m <= m+2.5 and end_m >= m+2.5
)
as perp_x		
		
from original_points inner join runs on start_chainage<=m and m <= end_chainage
)
    
'''    
        runQuery(query = insertQuery,db=db)
        db.commit()
    
    
    
    #update corrected_points.
    #update gcps table.
    
    def applyCorrections(self):
        q = runQuery(query = ''' select m,left_offset,st_asText(st_linemerge(ST_Collect(line))),st_x(pt) as x,st_y(pt) as y
        from corrections_m inner join lines on st_distance(line,pt) < 20
        group by pk
        order by m
    ''')
    
        while q.next():
            q.value(0)
            wkt = q.value(2)
            if wkt is not None:
                g = QgsGeometry.fromWkt(wkt)
                pt = QgsGeometry.fromPointXY(QgsPointXY(q.value(3),q.value(4)))
                #print(g)
                for part in g.parts():#QgsLineString
                #doesn't seem to be easy way to locate point on QgsLinestring. Really?
                    line = QgsGeometry.fromWkt(part.asWkt())#QgsGeometry#LineStringZ
                    print(line)
                    p = line.nearestPoint(pt)
                    print(p)#QgsGeometry: Point x,y
    
    #find m shift that minimises distance to point and neiboring corrections.
    
    
    def rechainage(self,resolution=0.01):
        if self.geom is not None:
            self.geom.rechainage(resolution)


    def _uploadGeom(self):
        if self.geom is not None:
            db = defaultDb()
            db.transaction()
            runQuery(db=db,query='delete from corrected_points')
            q = QSqlQuery(db)
            if q.prepare('insert into corrected_points(m,pt) values (:m,makePoint(:x,:y,27700))'):
                for i,v in enumerate(self.geom.m):
                    q.bindValue(':m',float(v))
                    q.bindValue(':x',float(self.geom.x[i]))
                    q.bindValue(':y',float(self.geom.y[i]))
                    if not q.exec():
                        raise queryError(q)
                runQuery(db=db,query='update corrected_points set next_id = (select id from corrected_points as np where np.m>corrected_points.m order by np.m limit 1)')
            else:
                raise queryPrepareError(q)


    #download original m,x,y and new m,x,y
    def _downloadGeom(self,minM=None,maxM=None):
        try:
            #query = 'select m,st_x(pt),st_y(pt) from original_points {filt} order by m'
            filt = ''
            if minM is not None:
                filt += 'where m>= :minM'
            q = runQuery('select m,st_x(pt),st_y(pt) from corrected_points order by m')
            m = []
            x = []
            y = []
            while q.next():
                m.append(q.value(0))
                x.append(q.value(1))
                y.append(q.value(2))
            self.geom = splineStringM(points(m,x,y))
        except Exception as e:
            self.geom = None
            print(e)
            
        try:
            #query = 'select m,st_x(pt),st_y(pt) from original_points {filt} order by m'
            filt = ''
            if minM is not None:
                filt += 'where m>= :minM'
            q = runQuery('select m,st_x(pt),st_y(pt) from original_points order by m')
            m = []
            x = []
            y = []
            while q.next():
                m.append(q.value(0))
                x.append(q.value(1))
                y.append(q.value(2))
            self.originalGeom = splineStringM(points(m,x,y))
        except Exception as e:
            self.originalGeom = None
            print(e)            

    
    
    #linestring of original_points from startM to endM. ends interpolated. reverse direction where startM>endM 
    #->QgsGeometry
    @staticmethod
    def originalLine(startM,endM,maxPoints = 2000):
        #MakeLine returns null with CastToXY. bug in spatialite?
        lineQuery = '''
        select
        st_asText(MakeLine(pt)),count(pt)
        from
        (
        select m,pt from original_points where :s < m and m < :e
        union 
        select :s as m,makePoint(st_x(Line_Interpolate_Point(line,(:s-start_m)/(end_m-start_m))),st_y(Line_Interpolate_Point(line,(:s-start_m)/(end_m-start_m))),27700) as pt 
        from lines where start_m <= :s and end_m >= :s
        UNION
        select :e as m,makePoint(st_x(Line_Interpolate_Point(line,(:e-start_m)/(end_m-start_m))),st_y(Line_Interpolate_Point(line,(:e-start_m)/(end_m-start_m))),27700) as pt 
        from lines where start_m <= :e and end_m >= :e order by m {d}) a
        '''
        if startM>endM:
            v = {':s':endM,':e':startM}
            lineQuery = lineQuery.format(d = 'desc')
        else:
            v = {':s':startM,':e':endM}
            lineQuery = lineQuery.format(d = 'asc')
     #   print(lineQuery)
        q = runQuery(query = lineQuery,values = v)
        while q.next():
            wkt = q.value(0)
            if q.value(1) < maxPoints:
             #   print('wkt',wkt)
                if isinstance(wkt,str):
                    return QgsGeometry.fromWkt(wkt)
        return QgsGeometry()
    
    
    #way harder than it should be.
    #no way to split multilinestring in spatialite.
    #linemerge drops m value
    #view with longer lines ~10m?
    #QgsPointXY -> [(chainage:float,offset:float)]
    @staticmethod
    def possibleChainages(pt,dist=20):
        #1 possible chainage,offset per run...
        query = '''
        select s+(e-s)*Line_Locate_Point(line,makePoint(:x,:y)) as m
        ,st_distance(line,makePoint(498522,363010)) as dist
        from lines_5 where st_intersects(line,st_buffer(makePoint(:x,:y),:d))
        order by dist
        '''
        q = runQuery(query = query,
        values = {':x':pt.x(),':y':pt.y(),':d':dist})
        r = []
        while q.next():
            r.append((q.value(0),q.value(1)))
        return r
    
        
        
#can call static methods like function with ClassName.method_name()
if __name__ == '__console__':
    v = gpsModel.possibleChainages(QgsPointXY(498522,363010))
    print(v)
    