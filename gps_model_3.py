# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:44:42 2023

@author: Drew.Bennett

rectangular images

"""

import csv
import os
import numpy as np
from qgis.core import QgsGeometry,QgsPointXY
#from PyQt5.QtCore import pyqtSignal

from image_loader.db_functions import runQuery,defaultDb,queryError,queryPrepareError
from image_loader.dims import WIDTH,HEIGHT,LINES,PIXELS,offsetToPixel,mToLine
from image_loader.geometry_functions import fractionAndOffset,magnitude

from PyQt5.QtSql import QSqlQuery

from osgeo.osr import SpatialReference, CoordinateTransformation,OAMS_TRADITIONAL_GIS_ORDER


maxM = 9999999999999999.9

#transform for parsing csv
epsg4326 = SpatialReference()
epsg4326.ImportFromEPSG(4326)
epsg4326.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)
#version dependent bad design.
#without this some gdal versions expect y arg to TransformPoint before x
epsg27700 = SpatialReference()
epsg27700.ImportFromEPSG(27700)
transform = CoordinateTransformation(epsg4326,epsg27700)

def parseCsv(file):
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        for i,d in enumerate(reader):
            try:
                m = round(float(d['Chainage (km)'])*1000)# need round to avoid floating point errors like int(1.001*1000) = 1000
                lon = float(d['Longitude (deg)'])
                lat = float(d['Latitude (deg)'])
                x,y,z = transform.TransformPoint(lon,lat)
                yield m,x,y
            except:
                pass
            
            
class gpsModel:
    
    #chainageRangeChanged = pyqtSignal()
    
    def __init__(self):
        pass


    @staticmethod        
    def clear():
        runQuery(query='delete from original_points')

        
    @staticmethod        
    def loadFile(file):
        ext = os.path.splitext(file)[1]
        if ext == '.csv':
            gpsModel.setValues(parseCsv(file))
            
            
    @staticmethod
    def setValues(vals):
        db = defaultDb()
        db.transaction()
        runQuery(query='delete from original_points',db=db)
        q = QSqlQuery(db)
        if not q.prepare('insert into original_points(m,pt) values (:m,makePoint(:x,:y,27700))'):
            raise queryPrepareError(q)
        for i,v in enumerate(vals):
            try:
                q.bindValue(':m',v[0])
                q.bindValue(':x',v[1])
                q.bindValue(':y',v[2])
                if not q.exec():
                    raise queryError(q)
            except Exception as e:
                message = 'error loading row {r} : {err}'.format(r = i,err = e)
                print(message)
        runQuery('update original_points set next_id = (select id from original_points as np where np.m>original_points.m order by np.m limit 1)',db=db)
        runQuery('update original_points set next_m = (select m from original_points as np where np.m>original_points.m order by np.m limit 1)',db=db)
        db.commit()
    
    
    
    @staticmethod
    def getPoint(m,offset):
        return QgsPointXY()
    
    
    
    @staticmethod
    def gcps(self,frame):
        pass
    
    
    
    @staticmethod
    def setCorrections(corrections):
        pass
    
    
    
    #->(pixel,line)
    #from corrected points.
    @staticmethod
    def pixelLine(point,frameId):
        v = gpsModel.locatePointCorrected(point,minM = frameId*HEIGHT,maxM=(frameId+1)*HEIGHT)
        if v:
            m,offset = v[0]
      #  print('m',m,'offset',offset)
            return (offsetToPixel(offset),mToLine(m,frameId))
    
    
    
    #use for correction dialog.
    #could use for GCPs
    @staticmethod    
    def pointFromPixelLine(pixel,line,frame):
        return QgsPointXY()
    
    
    
    @staticmethod    
    def originalPoint(m,offset):
        return QgsPointXY()
    
    
    
    #list of (m,offset) in ascending order of distance
    #m is closest point and doesn't depend on offset handling
    @staticmethod
    def locatePointOriginal(point,minM=0,maxM=maxM,maxDist = 10.0):
      x = point.x()
      y = point.y()
      point = np.array([x,y],dtype=np.double)
      
      #lines starting within maxDist square of point. good enough where maxDist >> line_length
      q = '''select p.m,st_x(p.pt),st_y(p.pt),n.m as next_m,st_x(n.pt) as next_x,st_y(n.pt) as next_y from 
      original_points as p inner join original_points as n on n.id = p.next_id
      and ST_Distance(MakeLine(p.pt,n.pt),makePoint(:x,:y,27700)) < :d
      and :minM <= n.m and p.m <= :maxM
      order by p.m
      '''
     
      query = runQuery(q,values = {':x':x,':y':y,':d':maxDist,':minM':minM,':maxM':maxM})
      lastEnd = None
      mod = []#m,offset,dist
      while query.next():
          start = np.array([query.value(1),query.value(2)])
          end = np.array([query.value(4),query.value(5)])
          
          f,offset = fractionAndOffset(start,end,point)
          m = query.value(0) + (query.value(3)-query.value(0)) * f
          
          if f < 0:
              dist = magnitude(start-point)
          if 0 <= f and f <= 1:
              dist = abs(offset)
          if f > 1:
              dist = magnitude(end-point) 
              
          startM = query.value(0)
          if startM != lastEnd:
              mod.append((m,offset,dist))
          else:
              if dist < mod[-1][2]:
                  mod[-1] = (m,offset,dist)
          
          lastEnd = query.value(3)
              
      return [(row[0],row[1]) for row in sorted(mod, key=lambda x: x[2])]#sort by distance        
    
    
    
    #list of (m,offset) in ascending order of distance
    #m is closest point and doesn't depend on offset handling
    @staticmethod
    def locatePointCorrected(pt,minM=0,maxM=maxM,maxDist = 10.0):
      x = pt.x()
      y = pt.y()
      point = np.array([x,y],dtype=np.double)
      
      #lines starting within maxDist square of point. good enough where maxDist >> line_length
      q = '''select p.m,st_x(p.pt),st_y(p.pt),n.m as next_m,st_x(n.pt) as next_x,st_y(n.pt) as next_y from 
      corrected_points as p inner join corrected_points as n on n.id = p.next_id
      and ST_Distance(MakeLine(p.pt,n.pt),makePoint(:x,:y,27700)) < :d
      and :minM <= n.m and p.m <= :maxM
      order by p.m
      '''
     
      query = runQuery(q,values = {':x':x,':y':y,':d':maxDist,':minM':minM,':maxM':maxM})
      lastEnd = None
      mod = []#m,offset,dist
      while query.next():
          start = np.array([query.value(1),query.value(2)])
          end = np.array([query.value(4),query.value(5)])
          
          f,offset = fractionAndOffset(start,end,point)
          m = query.value(0) + (query.value(3)-query.value(0)) * f
          
          if f < 0:
              dist = magnitude(start-point)
          if 0 <= f and f <= 1:
              dist = abs(offset)
          if f > 1:
              dist = magnitude(end-point) 
              
          startM = query.value(0)
          if startM != lastEnd:
              mod.append((m,offset,dist))
          else:
              if dist < mod[-1][2]:
                  mod[-1] = (m,offset,dist)
          
          lastEnd = query.value(3)
              
      return [(row[0],row[1]) for row in sorted(mod, key=lambda x: x[2])]#sort by distance     


    
    @staticmethod
  #performance unimportant.
    def originalLine(startM,endM,maxPoints = 2000):
    
        if startM < endM:
            s = startM
            e = endM
        else:
            s = endM
            e = startM
    
        q = '''select :s
                ,last.x + (st_x(next.pt)-last.x)*(:s - last.m)/(next.m-last.m)
                ,last.y + (st_y(next.pt)-last.y)*(:s - last.m)/(next.m-last.m)
                from
                (select m,st_x(pt) as x,st_y(pt) as y,next_m from original_points where m <= :s and next_m > :s) last
                inner join original_points as next on next.m = last.next_m
        union		
        select m,st_x(pt),st_y(pt) from original_points where :s<= m and m <= :e
        UNION
        select :e
                ,last.x + (st_x(next.pt)-last.x)*(:e - last.m)/(next.m-last.m)
                ,last.y + (st_y(next.pt)-last.y)*(:e - last.m)/(next.m-last.m)
                from
                (select m,st_x(pt) as x,st_y(pt) as y,next_m from original_points where m <= :e and next_m > :e) last
                inner join original_points as next on next.m = last.next_m
        order by m
        limit {maxPoints}
        '''.format(maxPoints=maxPoints)
        
        q = runQuery(q,values={':s':s,':e':e})
        p = []
        while q.next():
            p.append((q.value(1),q.value(2)))
            
        if p:
            if startM>endM:
                p = reversed(p)
            return QgsGeometry.fromPolylineXY([QgsPointXY(i[0],i[1]) for i in p])
        
        return QgsGeometry()

    @staticmethod
    def rowCount():
        q = runQuery('select count(m) from original_points')
        while q.next():
            return q.value(0)


    #(min,max) chainage
    @staticmethod
    def originalChainageRange():
        q = runQuery('select min(m),max(m) from original_points')
        while q.next():
            return (q.value(0),q.value(1))


    @staticmethod
    #frame from corrected position
    def getFrame(point,startM = 0 ,endM=maxM):
        opts = gpsModel.locatePointOriginal(point,minM = startM,maxM = endM)
        if opts:
            m,offset = opts[0]
            if np.isfinite(m):
                return int(np.ceil(m/HEIGHT))
        return -1
        
        
    @staticmethod
    def hasGps():
        return gpsModel.rowCount() > 0
        
        