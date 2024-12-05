# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:52:57 2023

@author: Drew.Bennett


linestringM with quadratic or cubic spline. 

1 point: 1 m+offset since derivitive is continuous


"""
from qgis.core import QgsFeature,QgsGeometry,edit,QgsPointXY
from qgis.utils import iface
from image_loader.layer_styles.styles import centerStyle
from image_loader.db_functions import runQuery
from image_loader.dims import HEIGHT,LINES,PIXELS,WIDTH,frameToM,mToFrame
from image_loader.gps_interface import gpsInterface

K = 3
S = 0
N = 2

import numpy as np
from image_loader.splinestring import splineString





class gpsModel(gpsInterface,splineString):
    
    
    def __init__(self):
        splineString.__init__(self)
        self.download()

    def loadFile(self,file,startAtZero = True):
        gpsInterface.loadFile(file = file,startAtZero = startAtZero)
        self.download()
        
        
    def clear(self):
        super().clear()
        self.download()
        
        
    def download(self):
        q = runQuery('select m,st_x(pt),st_y(pt) from original_points group by m having count(m)=1  order by m')
        m = []
        x = []
        y = []
        while q.next():
            m.append(q.value(0))
            x.append(q.value(1))
            y.append(q.value(2))
        splineString.setValues(self,np.transpose(np.array([m,x,y],dtype = float)))#gpsInterface also has setValues method
    #    print('downloaded',self.xSpline)
      
    
    def line(self,startM,endM,startOffset = 0,endOffset = 0):
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
            
        #    print('mo',mo)
            
            xy = self.point(mo)
            if len(xy)>0:
                if startM <= endM:
                    return QgsGeometry.fromPolylineXY([QgsPointXY(row[0],row[1]) for row in xy])
                else:
                    return QgsGeometry.fromPolylineXY([QgsPointXY(row[0],row[1]) for row in xy[::-1]])

        return QgsGeometry()
   

    #start of uncorrected frame
    #->int
    @staticmethod
    def pointToFrame(point,maxDist = 10):
        if gpsInterface.tableHasGps():
            qs = '''
            select start_m+(end_m-start_m)*line_locate_point(line,makePoint(:x,:y,27700)) as m
            from original_lines where distance(line,makePoint(:x,:y,27700)) <= :d
            order by distance(line,makePoint(:x,:y,27700))
            limit 1'''
            q = runQuery(qs,values={':x':point.x(),':y':point.y(),':d':maxDist})
            while q.next():
                m = q.value(0)
                return mToFrame(m)
        return -1


    #qgsPointXY for start of uncorrected frame
    @staticmethod    
    def frameToPoint(frame):
        if gpsInterface.tableHasGps():
            qs = '''select st_x(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
            ,st_y(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
             from original_lines
             where end_m >= :m - 0.0001 and start_m < :m + 0.0001 limit 1'''
            q = runQuery(qs,values={':m':frameToM(frame)})
            while q.next():
                return QgsPointXY(q.value(0),q.value(1))
        return QgsPointXY()
    
    
    @staticmethod
    def getCorrection(frame):
        q = runQuery(query = 'select chainage_shift,offset from runs_view where start_frame <= :f and end_frame >= :f order by start_frame limit 1',values = {':f':frame})
        while q.next():
            return (q.value(0),q.value(1))
        
            
    #-> [(x,y,pixel,line)]
    def gcps(self,frame):
        if self.hasGps():
            chainageShift,offset = self.getCorrection(frame)
            startM = frameToM(frame) + chainageShift
            endM = startM + HEIGHT
            mo = np.zeros((N*2,2)) * np.nan
            mo[:,0][0:N] = np.linspace(startM,endM,N)
            mo[:,0][N:] = np.linspace(startM,endM,N)
            mo[:,1][0:N] = offset + WIDTH/2
            mo[:,1][N:] = offset - WIDTH/2
       #     print('mo',mo)
            xy = self.point(mo)
            r = np.zeros((N*2,4)) * np.nan
            r[:,0:2] = xy
            r[:,2][0:N] = 0
            r[:,2][N:] = PIXELS
            r[:,3][0:N] = np.linspace(LINES,0,N)
            r[:,3][N:] = np.linspace(LINES,0,N)
         #   print('gcps.r',r)
            return [(row[0],row[1],int(row[2]),int(row[3])) for row in r]
        
 
    def hasGps(self):
        return self.hasPoints()
    

    def makeLayer(self,corrected = False):
        uri = "LineString?crs=epsg:27700&field=run:int&field=frame:int&field=start_chain:int&field=end_chain:int&index=yes"
        if corrected:
            name = 'corrected_GPS'
        else:
            name = 'original_GPS'
        layer = iface.addVectorLayer(uri, name, "memory")
        fields = layer.fields()
            
        def features():
            for i in range(0,int(self.maxM()/HEIGHT)+1):
                frame = i+1
                startChain = i * HEIGHT
                endChain = startChain + HEIGHT
                geom = self.line(startChain,endChain)
                #print('geom',geom)
                f = QgsFeature(fields)
               # f['run'] = q.value(0)
                f['frame'] = frame
                f['start_chain'] = startChain
                f['end_chain'] = endChain
                f.setGeometry(geom)
                if f.isValid():
                    yield f
    
        with edit(layer):
             layer.addFeatures(features())
        layer.loadNamedStyle(centerStyle)    
    
    
    
    
    
if __name__ in ('__console__'):
    m = gpsModel()
  #  mo = np.array([(0,0),(100,5),(200,10)])
  #  print('perp',m.leftPerp(mo[:,0]))
  #  print(m.point(mo))
 #   frame = 2703
  #  print('gcp',m.gcps(frame))
    
    p = QgsPointXY(354456.522,321920.860)
    loc = m.locate(p)
    print('loc',loc)