# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 11:44:13 2023

@author: Drew.Bennett
"""

from image_loader.splinestring import splineStringM,points
from image_loader.db_functions import defaultDb,runQuery,queryError,queryPrepareError
from qgis.core import QgsPointXY
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
#offset -> width/2 pixel->0


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
    
    
    #update gcps table
    def updateGCP(self):
        if self.geom is not None:
            db = defaultDb()
            db.transaction()
            runQuery('delete from gcp',db=db)
            runQuery('insert into gcp (frame,pixel,line,pt) select frame_id,pixel,line,makePoint(new_x,new_y,27700) from corrections',db=db)
            imagesQuery = runQuery('select image_id from images',db=db)#could add where marked here.
            q = QSqlQuery(db)
            if not q.prepare('insert into gcp(frame,pixel,line,pt) values (:frame,:pixel,:line,makePoint(:x,:y,27700))'):
                raise queryError(q)
            while imagesQuery.next():
                frameId = imagesQuery.value(0)
                for line in [0,LINES]:
                    for pixel in [0,PIXELS]:
                        pt = self.getPoint(frameId,pixel,line)
                        q.bindValue(':frame',frameId)
                        q.bindValue(':pixel',pixel)
                        q.bindValue(':line',round(line))
                        q.bindValue(':x',pt.x())
                        q.bindValue(':y',pt.y())
                        if not q.exec():
                            raise queryError(q)
            db.commit()


    def clear(self):
        runQuery('delete from corrected_points')
        runQuery('delete from original_points')
        self._downloadGeom()
        
    #uncorrected
    #tuple. chainage,left_offset
    def getPoint(self,frameId,pixel,line):
        if self.geom is not None:
            ch = frameId*5-HEIGHT*line/LINES
            offset = _pixelToOffset(pixel)
            try:
                xy = self.geom.interpolatePoints([ch],[offset])
                return QgsPointXY(xy[0],xy[1])
            except Exception as e:
                print(e)
                return QgsPointXY()
    
    
    def getFrame(self,point):
        if self.run is not None:
            mQuery = '''
            select start_m+(end_m-start_m)*Line_Locate_Point(line,makePoint(:x,:y,27700))  
            from corrected_lines where start_m <= (select max(image_id)*5-5 from images where run = :run) 
                                                   and end_m>=  (select min(image_id)*5-5 from images where run = :run) 
                                                   order by ST_Distance(line,makePoint(:x,:y,27700)) 
                                                   limit 1
            '''
            q = runQuery(mQuery,values = {':run':self.run,':x':point.x(),':y':point.y()})
            while q.next():
                m = asFloat(q.value(0))
                if m is not None:
                    return numpy.floor(m/HEIGHT)+1
        else:
            print('getFrame: no run set')
    
    
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
    
    
    def applyCorrections(self):
        if self.geom is not None:
            correctionQuery = '''select 5*(frame_id-line/1250.0) as m
            ,new_x
            ,new_y
            ,pixel
            from corrections
            order by m
            '''
            m = []
            newX = []
            newY = []
            offset = []
            q = runQuery(correctionQuery)
            while q.next():
                m.append(q.value(0))
                newX.append(q.value(1))
                newY.append(q.value(2))
                offset.append(_pixelToOffset(q.value(3)))
                
            if len(m)>0:    
                m = numpy.array(m)
                newPoints = numpy.stack([numpy.array(newX),numpy.array(newY)])
                oldPoints = self.geom.interpolatePoints(m,offset)#2 rows top is x bottom is y.
                XYShifts = newPoints - oldPoints
                #print('x',self.geom.x + numpy.interp(self.geom.m,m,XYShifts[0]))
                self.geom.setPoints(points(m = self.geom.m,
                                           x = self.geom.x + numpy.interp(self.geom.m,m,XYShifts[0]),
                                           y = self.geom.y + numpy.interp(self.geom.m,m,XYShifts[1])))
                self._uploadGeom()


    def rechainage(self,resolution=0.01):
        if self.geom is not None:
            self.geom.rechainage(resolution)


    def _uploadGeom(self):
        if self.geom is not None:
            print(self.geom.x)
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


