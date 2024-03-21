# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 10:52:57 2023

@author: Drew.Bennett


linestringM with quadratic or cubic spline. 

1 point: 1 m+offset since derivitive is continuous


"""
from scipy import interpolate
from scipy.optimize import minimize_scalar
from qgis.core import QgsGeometry, QgsPointXY
from qgis.core import QgsFeature,QgsGeometry,edit
from qgis.utils import iface
from image_loader import db_functions
from image_loader.layer_styles.styles import centerStyle
from image_loader.dims import HEIGHT



from image_loader.db_functions import runQuery
from image_loader.dims import (HEIGHT,LINES,PIXELS,offsetToPixel, pixelToOffset,WIDTH,frameToM,mToFrame,MAX,clamp,vectorizedMToLine,vectorizedOffsetToPixel)

from image_loader.gps_interface import gpsInterface

K = 3
S = 0
N = 2

import numpy as np

#numpy array. m,x,y
#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5



def leftPerp(vect):
    return np.array([vect[1],-vect[0]])


#[(x,y)] or ()
def to2DArray(x,y):
    return np.array([[x,y]],dtype = float)


class gpsModel(gpsInterface):
    
    
    def __init__(self):
        self.download()


    def loadFile(self,file,startAtZero = True):
        super().loadFile(file = file,startAtZero = startAtZero)
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
        self.m = np.array(m)
        self.x = np.array(x)
        self.y = np.array(y)
        
        if len(self.m) >= K:
            self.xSpline = interpolate.UnivariateSpline(self.m, self.x , s = S, ext='const', k = K)
            self.ySpline = interpolate.UnivariateSpline(self.m, self.y , s = S, ext='const', k = K)
            self.xDerivitive = self.xSpline.derivative(1)
            self.yDerivitive = self.ySpline.derivative(1)    
        else:
            self.xSpline = None
            self.ySpline = None
            self.xDerivitive = None
            self.yDerivitive = None
            
    # array[[x,y]] or []
    def point(self,mo):
        if self.hasGps():
            m = mo[:,0]
            r = np.zeros((len(m),2)) * np.nan
            r[:,0] =  self.xSpline(m)
            r[:,1] = self.ySpline(m)
            offsets = mo[:,1]
          #  if not np.any(offsets):
            perps = self.leftPerp(m)#([x],[y])
            r[:,0] = r[:,0] + perps[:,0] * offsets
            r[:,1] = r[:,1] + perps[:,1] * offsets
            return r
        return []
    
    #convert geometry in terms of m,offset to x,y
    #QgsGeometry
    # x as m. y as offset
    
    def moGeomToXY(self,geom,mShift = 0.0,offset = 0.0):
        g = QgsGeometry(geom)
        mo = []
        for i,v in enumerate(g.vertices()):
            mo.append([v.x()+mShift,v.y()+offset])
           # p = to2DArray(v.x()+mShift,v.y()+offset)
        mo = np.array(mo)
        new = self.point(mo)
        for i,row in enumerate(new):
            g.moveVertex(row[0],row[1],i)
        return g
    
    
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
    
    
    def locate(self,point,mRange = (0,MAX) ,maxDist = 10):
        #find line segments within buffer of points
        #numerical methods to find closest point of splines to points
        qs = '''select max(start_m,:s),min(end_m,:e) from original_lines 
        where st_distance(line,makePoint(:x,:y,27700)) < :md and start_m <= :e and end_m >= :s
        order by start_m
        '''
    #    q = runQuery('select m,st_x(pt),st_y(pt) from original_points order by m')
        q = runQuery(qs,values = {':md':maxDist,':x':point.x(),':y':point.y(),':s':mRange[0],':e':mRange[1]})
        
        last = None
        ranges = []
        while q.next():
            startM = q.value(0)
            endM = q.value(1)
            if last != startM:
                ranges.append([startM,endM])
            else:
                ranges[-1][1] = endM
            last = endM
        
     #   print('ranges',ranges)
        
        def _dist(m):
            mo = np.array([[m,0]])
         #   print('mo',mo)
            p = self.point(mo)
         #   print('p',p)
            if len(p)>0:
                pt = QgsPointXY(p[0,0],p[0,1])
                return pt.distance(point)
           # print('dist',pt.distance(point))
            return MAX
        
        
        
        r = np.zeros((len(ranges),3))
        for i,row in enumerate(ranges):
            res = minimize_scalar(_dist,bounds = (row[0],row[1]),method='bounded')
            m = res.x
            r[i,0] = m
        
        #vector from centerLine to point
        centerVect = self.point(r)
        centerVect[:,0] = point.x() - centerVect[:,0]
        centerVect[:,1] = point.y() - centerVect[:,1]
        
        perps = self.leftPerp(r[:,0])
        
        for i,row in enumerate(perps):
            r[i,1] = np.dot(row,centerVect[i])
        r[:,2] = abs(r[:,1])
    #    print('r',r)
        r = r[r[:, 2].argsort()]# sort by column 2        
        return r[:,[0,1]]

   

        
    
        
    #perpendicular unit vectors at m
    def leftPerp(self,m):
        if self.hasGps():
            r = np.zeros((len(m),2)) * np.nan
            dx = self.xDerivitive(m)
            dy = self.yDerivitive(m)
            magnitudes = np.sqrt(dx*dx+dy*dy)
            r[:,0] = -dy/magnitudes
            r[:,1] = dx/magnitudes
            return r


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
        return len(self.m) > 0


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