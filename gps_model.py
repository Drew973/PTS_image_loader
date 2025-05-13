# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:52:57 2023

@author: Drew.Bennett


linestringM with quadratic or cubic spline. 

1 point: 1 m+offset since derivitive is continuous


"""
import numpy as np
from qgis.core import QgsFeature,QgsGeometry,edit,QgsPointXY,QgsVectorLayer,QgsProject
from image_loader.db_functions import runQuery
from image_loader import settings,dims
from image_loader.backend import gps_functions
from image_loader import type_conversions
from qgis.core import QgsCoordinateReferenceSystem




def getCorrection(frame):
    q = runQuery(query = 'select chainage_shift,offset from runs_view where start_frame <= :f and end_frame >= :f order by start_frame limit 1',values = {':f':frame})
    while q.next():
        return (q.value(0),q.value(1))
    return (0.0 , 0.0)
    



class gpsModel:
    
    
    def __init__(self):
        self.splineString = None
        self.error = ''
        self.setSrid(settings.destSrid())


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


    def moGeomToXY(self,g,mShift,offset):
        return self.splineString.moGeomToXY(g,mShift,offset)


    def clear(self) -> None:
        gps_functions.clear()
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
   


if __name__ in ('__console__'):
    m = gpsModel()
    p = QgsPointXY(354456.522,321920.860)
    loc = m.locate(p)
    print('loc',loc)