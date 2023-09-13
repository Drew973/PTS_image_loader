# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 11:44:13 2023

@author: Drew.Bennett
"""

from image_loader.splinestring import splineStringM
from image_loader.db_functions import defaultDb,runQuery,queryError
from qgis.core import QgsPointXY
from PyQt5.QtSql import QSqlQuery
import csv
import math
import numpy


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


def loadGps(file,db=None):
    if db is None:
        db = defaultDb()

    db.transaction()
        
    runQuery(db=db,query='delete from points')
    
    q = QSqlQuery(db)
    if not q.prepare('insert into points(m,pt) values(:m,st_transform(MakePoint(:x,:y,4326),27700))'):
        raise queryError(q)
    
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        
        for i,d in enumerate(reader):
        #   pt = transform.transform(QgsPointXY(float(d['Longitude (deg)']),float(d['Latitude (deg)'])))
        
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
                
    runQuery(db=db,query='update points set next_m = (select m from points as np where np.m>points.m order by m limit 1),x = st_x(pt), y = st_y(pt)')
    runQuery(db=db,query='update points set corrected_x=x,corrected_y = y')
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
        self._sync()
    
    
    def hasGps(self):
        return self.geom is not None
    
    
    
    def loadFile(self,file):
        loadGps(file)
        self._sync()
        
    
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
            
                for line in [0,250,500,750,1000,1250]:
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

    
    #tuple. chainage,left_offset
    def getPoint(self,frameId,pixel,line):
        ch = frameId*5-HEIGHT*line/LINES
        offset = _pixelToOffset(pixel)
        try:
            xy = self.geom.interpolatePoint(ch,offset)
            return QgsPointXY(xy[0],xy[1])
        except Exception as e:
            print(e)
            return QgsPointXY()
    
    

    def getPixelLine(self,frameId,point):
        mQuery = '''
        select minm+Line_Locate_Point(geom,pt)*(maxm-minm) from
        (
        select makeLine(MakePointM(corrected_x,corrected_y,m)) as geom,min(m) as minm,max(m) as maxm,makePoint(:x,:y) as pt
        from points where :frame*5-5<=m and m <=:frame*5
        order by m) line
        '''
        q = runQuery(mQuery,values = {':frame':frameId,':x':point.x(),':y':point.y()})
        while q.next():
        #    print('m',q.value(0))
            m = asFloat(q.value(0))
            if m is not None:
                nearest = self.geom.interpolatePoint(m)
                shortest = numpy.array([point.x()-nearest[0],point.y()-nearest[1]])#nearestPoint on centerline -> point
                perp = self.geom.leftPerp(m)
            #    print('perp',perp)
                offset = numpy.dot(shortest,perp)
            #    print(offset)
                return (_offsetToPixel(offset),_line(m=m,frame=frameId))
    
    
    def _sync(self):
        try:
            points = []
            q = runQuery('select m,corrected_x,corrected_y from points order by m')
            points = []
            while q.next():
                points.append((q.value(0),q.value(1),q.value(2)))
            self.geom = splineStringM(points)
        except:
            self.geom = None
