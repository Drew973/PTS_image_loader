# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:52:57 2023

@author: Drew.Bennett


linestringM with quadratic or cubic spline. 

1 point: 1 m+offset since derivitive is continuous
mypy gps_model.py --follow-imports=silent

"""
import numpy as np
from qgis.core import QgsFeature,QgsGeometry,edit,QgsPointXY,QgsVectorLayer,QgsProject,QgsCoordinateTransform
from image_loader.db_functions import runQuery,queryError,prepareQuery,createDb,bulkInsert
from image_loader import settings,dims,file_locations
from image_loader.splinestring import splineString
from image_loader import group_functions
from image_loader.backend import gps_functions
from image_loader import type_conversions
from qgis.core import QgsCoordinateReferenceSystem
from scipy.interpolate import splrep,PPoly
from PyQt5.QtSql import QSqlDatabase

import os
import csv

S = 0.5
K = 2


#make layer with centerlines.
#1 feature per frame.
#might have less than 1 point/frame if using shapefile geom.
# different results if reproject in QGIS vs in spatialite.experiment with this.
def makeGpsLayer(s : splineString) -> None:
    uri = "LineString?crs=epsg:{p}&field=frame:int&field=start_chain:int&field=end_chain:int&index=yes".format(p = settings.destSrid())    
    layer = QgsVectorLayer(uri,'original_GPS',"memory")
    
    fields = layer.fields()
    
    maxFrame = dims.mToFrame(gps_functions.maxM())
                             
                             
    def features():
        for frame in range(0,maxFrame+1):
            f = QgsFeature(fields)
            startChain = dims.frameToM(frame)
            endChain = startChain + dims.HEIGHT
            f['start_chain'] = startChain
            f['end_chain'] = endChain
            f['frame'] = frame
            points = s.centerLinePoint([startChain,endChain])#array [(x1,y1),(x2,y2)]
            geom = QgsGeometry.fromPolylineXY([QgsPointXY(points[0,0],points[0,1]),QgsPointXY(points[1,0],points[1,1])])
            f.setGeometry(geom)
            if f.isValid():
                yield f
                
    with edit(layer):
         layer.addFeatures(features())
    layer.loadNamedStyle(file_locations.centerStyle)
   # load_image.loadLayer(layer)
    group = group_functions.getGroup(['image_loader'])#QgsLayerTreeGroup
    group.addLayer(layer)

    node = group.findLayer(layer)
    node.setItemVisibilityChecked(True)
    node.setExpanded(False)        
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend




def getCorrection(frame) -> tuple[float,float]:
    q = runQuery(query = 'select chainage_shift,offset from runs_view where start_frame <= :f and end_frame >= :f order by start_frame limit 1',values = {':f':frame})
    while q.next():
        return (q.value(0),q.value(1))
    return (0.0 , 0.0)
    

#-> '-gcp <pixel> <line> <easting> <northing>'
#might as well serialize to string here. list is valid JSON and avoids passing "" to CLI
N = 2 # GCP points per side of frame
def calcGcps(frame : int , geom : splineString) -> str:
     chainageShift , offset = getCorrection(frame)
     startM = dims.frameToM(frame) + chainageShift
     endM = startM + dims.HEIGHT
     mo = np.zeros((N*2,2)) * np.nan
     mo[:,0][0:N] = np.linspace(startM,endM,N)
     mo[:,0][N:] = np.linspace(startM,endM,N)
     mo[:,1][0:N] = offset + dims.WIDTH/2
     mo[:,1][N:] = offset - dims.WIDTH/2
     xy = geom.point(mo)
     r = np.zeros((N*2,4)) * np.nan
     r[:,0:2] = xy
     r[:,2][0:N] = 0
     r[:,2][N:] = dims.PIXELS
     r[:,3][0:N] = np.linspace(dims.LINES,0,N)
     r[:,3][N:] = np.linspace(dims.LINES,0,N)
     #v = [(row[0],row[1],int(row[2]),int(row[3])) for row in r]
     #-gcp <pixel> <line> <easting> <northing> [<elevation>]
     return ' '.join(['-gcp {pixel} {line} {easting} {northing}'.format(pixel = int(a[2] ), line = int(a[3]) , easting = a[0] , northing = a[1]) for a in r])
     
    
    
    
    
#update x_spline and y_spline tables from original_points table for mfv number
#call after uploading GPS points or reprojecting.
def recalcSplineTable(db:QSqlDatabase , mfv:str):
    db.transaction()
    runQuery('delete from x_spline where mfv_number = :mfv', values = {':mfv':mfv} , db = db)
    runQuery('delete from y_spline where mfv_number = :mfv', values = {':mfv':mfv} , db = db)

    
    mVals = []
    xVals = []
    yVals = []
    q = runQuery('select m,x,y from original_points order by m' , db = db)
    while q.next():
        mVals.append(q.value(0))
        xVals.append(q.value(1))
        yVals.append(q.value(2))
        
  
    #update x_spline table
    xSpline = PPoly.from_spline(splrep(x = mVals, y = xVals, s = S, k=K))#PPoly
  #  print(xSpline.c)# [...quadratic term,linear,constant]
  #  print(xSpline.x)# start m


    xQuery = prepareQuery('insert into x_spline(mfv_number,start_m,end_m,x0,x1,x2) values (:mfv,:start_m, :end_m, :x0 , :x1 ,:x2)' , db = db)


    for i,m in enumerate(xSpline.x[0:-1]):
        xQuery.bindValue(':mfv' , mfv)
        xQuery.bindValue(':start_m' , float(m))
        xQuery.bindValue(':end_m' , float(xSpline.x[i+1]))
        xQuery.bindValue(':x0' , float(xSpline.c.item(2,i)))
        xQuery.bindValue(':x1' , float(xSpline.c.item(1,i)))
        xQuery.bindValue(':x2' , float(xSpline.c.item(0,i)))
        if not xQuery.exec():
            raise queryError(xQuery)


    #update y_spline table
    ySpline = PPoly.from_spline(splrep(x = mVals, y = yVals, s = S, k=K))#PPoly
    yQuery = prepareQuery('insert into y_spline(mfv_number,start_m,end_m,y0,y1,y2) values (:mfv,:start_m, :end_m, :y0 , :y1 ,:y2)' , db = db)
    for i,m in enumerate(ySpline.x[0:-1]):
        yQuery.bindValue(':mfv' , mfv)
        yQuery.bindValue(':start_m' , float(m))
        yQuery.bindValue(':end_m' , float(ySpline.x[i+1]))
        yQuery.bindValue(':y0' , float(ySpline.c.item(2,i)))
        yQuery.bindValue(':y1' , float(ySpline.c.item(1,i)))
        yQuery.bindValue(':y2' , float(ySpline.c.item(0,i)))
        if not yQuery.exec():
            raise queryError(yQuery)


    db.commit()


#calculate and set x and y_spline for mfv from values
def setSpline(db:QSqlDatabase, mfv:str, values:list):
    db.transaction()
    runQuery('delete from x_spline where mfv_number = :mfv', values = {':mfv':mfv} , db = db)
    runQuery('delete from y_spline where mfv_number = :mfv', values = {':mfv':mfv} , db = db)
    mVals = [v.m for v in values]
    xVals = [v.x for v in values]
    yVals = [v.y for v in values]

  
    #update x_spline table
    #splrep returns BSpline from [x],[y],s,k
    #PPoly is piecewise polynomial.
    #
    xSpline = PPoly.from_spline(splrep(x = mVals, y = xVals, s = S, k=K))#PPoly
  #  print(xSpline.c)# [...quadratic term,linear,constant]
  #  print(xSpline.x)# start m


    xQuery = prepareQuery('insert into x_spline(mfv_number,start_m,end_m,x0,x1,x2) values (:mfv,:start_m, :end_m, :x0 , :x1 ,:x2)' , db = db)


    for i,m in enumerate(xSpline.x[0:-1]):
        xQuery.bindValue(':mfv' , mfv)
        xQuery.bindValue(':start_m' , float(m))
        xQuery.bindValue(':end_m' , float(xSpline.x[i+1]))
        xQuery.bindValue(':x0' , float(xSpline.c.item(2,i)))
        xQuery.bindValue(':x1' , float(xSpline.c.item(1,i)))
        xQuery.bindValue(':x2' , float(xSpline.c.item(0,i)))
        if not xQuery.exec():
            raise queryError(xQuery)


    #update y_spline table
    ySpline = PPoly.from_spline(splrep(x = mVals, y = yVals, s = S, k=K))#PPoly
    yQuery = prepareQuery('insert into y_spline(mfv_number,start_m,end_m,y0,y1,y2) values (:mfv,:start_m, :end_m, :y0 , :y1 ,:y2)' , db = db)
    for i,m in enumerate(ySpline.x[0:-1]):
        yQuery.bindValue(':mfv' , mfv)
        yQuery.bindValue(':start_m' , float(m))
        yQuery.bindValue(':end_m' , float(ySpline.x[i+1]))
        yQuery.bindValue(':y0' , float(ySpline.c.item(2,i)))
        yQuery.bindValue(':y1' , float(ySpline.c.item(1,i)))
        yQuery.bindValue(':y2' , float(ySpline.c.item(0,i)))
        if not yQuery.exec():
            raise queryError(yQuery)


    db.commit()
    
    
    
from typing import NamedTuple

class MXY(NamedTuple):
    m: int
    x: float
    y: float


#CSV in ESPG:4326
#meant for rutacd csvs. these are usually 1m intervals(slow)
def parseCsv(file : str , toSrid:int, interval = 5):
    with open(file, 'r') as f:
        transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem(4326) , QgsCoordinateReferenceSystem(toSrid) , QgsProject.instance())
        reader = csv.DictReader(f)
        for i , d in enumerate(reader):
            if i% interval == 0:
                try:
                    # need round to avoid floating point errors like int(1.001*1000) = 1000
                    m : int = round(float(d['Chainage (km)'])*1000)
                    lon = float(d['Longitude (deg)'])
                    lat = float(d['Latitude (deg)'])
                   # alt = float(d['Altitude (m)'])
                    p = transform.transform(QgsPointXY(lon,lat))#transformed point
                    yield MXY(m, p.x(), p.y())
                except Exception as e:
                    print(e)
                    pass





def getXY(db:QSqlDatabase, mfv:str, m:float):
    '''select
    (select x0+x1*(start_m-5)+x2*(start_m-5)*(start_m-5) from x_spline where mfv_number = 'MFV 01' and start_m<=5 and end_m >=5 limit 1) as x
    ,(select y0+y1*(start_m-5)+y2*(start_m-5)*(start_m-5) from y_spline where mfv_number = 'MFV 01' and start_m<=5 and end_m >=5 limit 1) as y
    '''


class gpsModel:
    
    
    def __init__(self , db:QSqlDatabase):
        self.splineString = None
        self.error = ''
        self.setSrid(settings.destSrid())
        self.db = db

   


    def loadGpsFile(self, file:str, mfv:str):
        ext = os.path.splitext(file)[1]
        db = self.db
        db.transaction()
        
        runQuery('update mfv set gps_file = :gps where mfv_ref = :mfv', db=db ,values={':gps':file,':mfv':mfv})
        #runQuery('delete from original_points where mfv', db=self.db ,values={':gps':file,':mfv':mfv})
        runQuery('delete from original_points where mfv_number = :mfv' ,db=db, values = {':mfv':mfv})

        if ext == '.csv':
            data = [r for r in parseCsv(file , toSrid= settings.destSrid())]
            bulkInsert(db = db , query = "insert into original_points(mfv_number,m,x,y) values ('{mfv}',?,?,?)".format(mfv = mfv),values = data,columnCount = 3)
        
        setSpline(db = db , mfv = mfv , values = data)
       # recalcSplineTable(db = self.db , mfv = mfv)
        db.commit()




    #project WGS84 points in database into scid and load into splineString. 
    def setSrid(self,srid) -> None:
        self.srid = srid
        self.crs = QgsCoordinateReferenceSystem()
        self.crs.createFromSrid(self.srid)
        try:
            gps_functions.reproject()
            self.splineString = gps_functions.getSplineString()
            #"No GPS. Is GPS data loaded?"
            self.error = ''
        except Exception as e:
            self.splineString = None
            self.error = str(e)


    def downloadGpsLayer(self) -> None:
        if self.pointCount() > 0:
            makeGpsLayer(self.splineString)
        else:
            raise ValueError('No GPS points. Is GPS loaded?')


    #only used by chainages dialog. speed unimportant.
    #start of frame. point in wgs84 / EPSG:4326
    #point in model crs
    def pointToFrame(self , point , maxDist : float = 10.0) -> int:
        #self.splineString.locate being unreliable. problem in numpy optimize or splineString?
        #print('x',point.x(),'y',point.y())
        #m , offset = self.splineString.locate(x = point.x() , y = point.y() , maxM = float(backend.maxM()) , tol = 2.0)
        #return dims.mToFrame(m)
        mVals = np.arange(0 , gps_functions.maxM() , dims.HEIGHT/4)
        xy = self.splineString.centerLinePoint(mVals)
        sqdif = (xy[:,0] - point.x())*(xy[:,0] - point.x()) + (xy[:,1] - point.y())*(xy[:,1] - point.y())
        return dims.mToFrame(mVals[np.argmin(sqdif)])


    #used by chainagesDialog.
    #QgsGeometry in model srid
    def centerLine(self , startM : float , endM : float)  -> QgsGeometry:
        xy = self.splineString.centerLinePoint(np.arange(startM , endM , dims.HEIGHT))#[(x1,y1),(x2,y2)...]
        return QgsGeometry.fromPolylineXY([QgsPointXY(row[0],row[1]) for row in xy])
    
    
    @staticmethod
    def pointCount() -> int:
        q = runQuery('select count(m) from original_points')
        while q.next():
            return int(q.value(0))
        raise queryError(q)

    def moGeomToXY(self,g,mShift,offset):
        return self.splineString.moGeomToXY(g,mShift,offset)


    def clear(self) -> None:
        gps_functions.clearGps()
        self.setSrid(self.srid)


    def locate(self , x : float , y : float , minM : float , maxM : float):
        m , offset = self.splineString.locate(x = x , y = y , maxM = maxM , minM = minM , tol = 0.01)
        if abs(offset) > type_conversions.asFloat(settings.value('maxOffset'),100.0):
            raise ValueError('Nearest m,offset {p} outside maximum offset'.format(p = (m,offset)))
        return np.array([(m,offset)])
        

    #used in find correction dialog.
    #centerline with ends at given offsets.
    def line(self , startM : float , endM : float , startOffset : float = 0 , endOffset : float = 0) -> QgsGeometry:
        if startM <= endM:
            s = startM
            so = startOffset
            e = endM
            eo = endOffset
        else:
            s = endM
            so = endOffset
            e = startM
            eo = startOffset
        #along centerline. perpendicular line joining to startOffset and endOffset 
        m = [s,s]#want point at s,0 and s,so
        q = runQuery('select m from original_points where m > :s and m < :e order by m limit 2000',values = {':s':float(s),':e':float(e)})
     #   print('s',s,'e',e)
        while q.next():
            m.append(q.value(0))
        m += [e,e]
       # print('m',m)
        if len(m) > 2:
            mo = np.zeros((len(m),2))
            mo[:,0] = m
            mo[0,1] = so
            mo[-1,1] = eo
            xy = self.splineString.point(mo)
            if len(xy)>0:
                if startM <= endM:
                    return QgsGeometry.fromPolylineXY([QgsPointXY(row[0],row[1]) for row in xy])
                else:
                    return QgsGeometry.fromPolylineXY([QgsPointXY(row[0],row[1]) for row in xy[::-1]])
        return QgsGeometry()
   
    
    # ground control points for frame. depends on correction.     
    #-> [(x,y,pixel,line)]
    def gcps(self , frame : int) -> str:
         return calcGcps(frame,self.splineString)
 



if __name__ in ('__console__'):
    m = gpsModel(db = createDb())
   # p = QgsPointXY(354456.522,321920.860)
  #  loc = m.locate(p)
  #  print('loc',loc)
  
  #tests
    #  db = createDb()
 #     recalcSplineTable(db = db , mfv = 'test')    
      
  
  
  