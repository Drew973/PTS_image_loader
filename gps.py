# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 14:02:27 2026

@author: Drew.Bennett


todo: move gps stuff into here and type check it.


mypy gps.py --follow-imports=silent
"""

from typing import NamedTuple,Iterable,Iterator
from scipy.interpolate import splrep,PPoly
from PyQt5.QtSql import QSqlDatabase
import csv
from qgis.core import QgsPointXY,QgsFeature,QgsGeometry,QgsFields,QgsVectorLayer,QgsProject,edit
from image_loader.db_functions import runQuery,prepareQuery,queryError
from image_loader.settings import transformToDestCrs
import numpy as np
from image_loader import dims,settings,group_functions
from scipy.optimize import minimize_scalar
from math import sqrt



K = 3 #better to avoid even values for numerical stability. need g1 continuity(k>1)
#K=2 with s=0.5 was giving rapidly changing gradients. causing unpredictable offset direction.
S = 0.5 # smoothing factor for splines

class MXY(NamedTuple):
    m: float
    x: float
    y: float


#CSV in ESPG:4326
#meant for rutacd csvs. these are usually 1m intervals(slow)
def parseCsv(file : str , interval = 5) -> Iterator[MXY]:
    with open(file, 'r') as f:
        transform = transformToDestCrs(4326)
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






class XY(NamedTuple):
    x: float
    y: float



class MO(NamedTuple):
    m: float
    offset: float


class gcp(NamedTuple):
    x: float
    y: float
    pixel: int
    line: int



#https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PPoly.html#scipy.interpolate.PPoly

class curve:
    __slots__ = ('xSpline', 'ySpline', 'maxM', 'minM')
    #define attributes here to prevent stored dict.
    #https://leapcell.io/blog/deep-dive-into-slots-optimizing-python-class-memory-usage

    def __init__(self,xSpline,ySpline):
        self.xSpline : PPoly = xSpline
        self.ySpline : PPoly =ySpline
        self.maxM : float = float(xSpline.x.max())
        self.minM : float = float(xSpline.x.min())
     #   self.xDerivitive = self.xSpline.derivative(1)
     #   self.yDerivitive = self.ySpline.derivative(1)



        
   # def upload(self, db:QSqlDatabase , mfv:str):
  #      pass

    @staticmethod
    def fromPoints(points: Iterable[MXY] , startAtZero = False)  -> 'curve':
        mVals = []
        xVals = []
        yVals = []
        for p in points:
            mVals.append(p.m)
            xVals.append(p.x)
            yVals.append(p.y)

        mArray = np.array(mVals)
        if startAtZero:
            mArray = mArray - mArray.min()
        #splrep returns BSpline from [x],[y],s,k
        #PPoly is piecewise polynomial.
        xSpline : PPoly = PPoly.from_spline(splrep(x = mArray, y = xVals, s = S, k=K),extrapolate=False)
        ySpline : PPoly = PPoly.from_spline(splrep(x = mArray, y = yVals, s = S, k=K),extrapolate=False)
        return curve(xSpline,ySpline)


    #single point on centerline
    def point(self,m:float) -> QgsPointXY:
        return QgsPointXY(float(self.xSpline(m)),float(self.ySpline(m)))
    
    
    
    # get point from m and offset
    def offsetPoint(self,m:float , offset:float) -> QgsPointXY:
        if m < self.minM:
            raise ValueError('chainage < minimum {minM}'.format(minM = self.minM))
        if m > self.maxM:
            raise ValueError('chainage > maximum {maxM}'.format(maxM = self.maxM))      
        lp = self.leftPerp(m)
        #print('offsetPoint',m,offset,lp)
        x = float(self.xSpline(m)) + offset * lp[0]
        y = float(self.ySpline(m)) + offset * lp[1]
        return QgsPointXY(x,y)
    
    
    
    #perpendicular unit vector at m
    #(x,y)
    def leftPerp(self,m:float) -> tuple[float,float]:
       #dy/dx = self.ySpline(m,nu = 1)/self.xSpline(m,nu = 1)
        dx = float(self.xSpline(m,nu = 1)) # x'(m)   # wrong direction for some m.
        dy = float(self.ySpline(m,nu = 1)) # y'(m)
        magnitude = sqrt(dx*dx+dy*dy)
        # -y'(m),x'(m) / magnitude
        #print('dx:{dx},dy:{dy},magnitude{magnitude}'.format(dx=dx,dy=dy,magnitude=magnitude))
        return (-dy/magnitude,dx/magnitude)###########wrong?
       
    
    @staticmethod
    def fromRutacd(path:str,startAtZero:bool = False) -> 'curve':
        return curve.fromPoints(points = parseCsv(path),startAtZero = startAtZero)
    
    
    @staticmethod
    #returns curve or raises error.
    #quotes around typehint to prevent error with curve being undefined until class fully defined
    def fromDatabase(db:QSqlDatabase , mfvNumber:str) -> 'curve':
        
        
        xBreakpoints = []
        xCoefficients = []
        xQuery = runQuery('select start_m,x0,x1,x2,x3 from x_spline where mfv_number = :mfv order by start_m',values = {':mfv':mfvNumber})
        
        while xQuery.next():
            xCoefficients.append((xQuery.value(4),xQuery.value(3),xQuery.value(2),xQuery.value(1)))
            xBreakpoints.append(xQuery.value(0))

        xCoefficients.pop()
        np.array(xCoefficients)
     #   print(len(xCoefficients),len(xBreakpoints))

        xSpline = PPoly(np.transpose(xCoefficients), np.transpose(xBreakpoints), extrapolate=False)
      
        yBreakpoints = []
        yCoefficients = []
        yQuery = runQuery('select start_m,y0,y1,y2,y3 from y_spline where mfv_number = :mfv order by start_m',values = {':mfv':mfvNumber})
        
        while yQuery.next():
            yCoefficients.append((yQuery.value(4),yQuery.value(3),yQuery.value(2),yQuery.value(1)))
            yBreakpoints.append(yQuery.value(0))

        yCoefficients.pop()
        ySpline = PPoly(np.transpose(yCoefficients), np.transpose(yBreakpoints), extrapolate=False)

       # print('fromDatabase')
        return curve(xSpline,ySpline)
        
        
       # points = []
     #   q = runQuery('select m,x,y from original_points where mfv_number = :mfv order by m',values = {':mfv':mfvNumber})
     #   while q.next():
     #       points.append(MXY(q.value(0),q.value(1),q.value(2)))
     #   if len(points) ==0:
     #       raise ValueError('no points where mfv_number = "{mfv}"'.format(mfv = mfvNumber))
     #   return curve.fromPoints(points)
    
    
    
    #iterator of features. for adding to layer.
    def features(self , fields:QgsFields , mfv:str) -> Iterator[QgsFeature]:
        maxFrame = dims.mToFrame(self.maxM)

        for frame in range(0,maxFrame+1):
            f = QgsFeature(fields)
            startChain = dims.frameToM(frame)
            endChain = startChain + dims.HEIGHT
            f['start_chain'] = startChain
            f['end_chain'] = endChain
            f['frame'] = frame
            f['mfv'] = mfv
           # points = s.centerLinePoint([startChain,endChain])#array [(x1,y1),(x2,y2)]
            points = [self.point(startChain),self.point(endChain)]
            geom = QgsGeometry.fromPolylineXY(points)
            f.setGeometry(geom)
            if f.isValid():
                yield f
    

    
    def upload(self, db:QSqlDatabase , mfvNumber:str):
        interval = 5.0
        
        db.transaction()
        
        #insert into original_points table
        runQuery('delete from original_points where mfv_number = :mfv',db = db,values = {':mfv':mfvNumber})
        q = prepareQuery('insert into original_points(mfv_number,m,x,y) values (:mfv,:m,:x,:y)')
        q.setForwardOnly(True)
       
        num = int((self.maxM-self.minM)/interval)
       
        for m in np.linspace(self.minM,self.maxM,num):
            p = self.point(m)
            q.bindValue(':mfv',mfvNumber)
            q.bindValue(':m',float(m))
            q.bindValue(':x',p.x())
            q.bindValue(':y',p.y())
            if not q.exec():
                raise queryError(q)

        #insert into x_spline table
        runQuery('delete from x_spline where mfv_number = :mfv',db = db,values = {':mfv':mfvNumber})
        xQuery = prepareQuery('insert into x_spline(mfv_number,start_m,end_m,x0,x1,x2,x3) values (:mfv,:start_m, :end_m, :x0 , :x1 ,:x2 , :x3)' , db = db)
    
        for i,m in enumerate(self.xSpline.x[0:-1]):
            xQuery.bindValue(':mfv' , mfvNumber)
            xQuery.bindValue(':start_m' , float(m))
            xQuery.bindValue(':end_m' , float(self.xSpline.x[i+1]))
            xQuery.bindValue(':x0' , float(self.xSpline.c.item(3,i)))
            xQuery.bindValue(':x1' , float(self.xSpline.c.item(2,i)))
            xQuery.bindValue(':x2' , float(self.xSpline.c.item(1,i)))
            xQuery.bindValue(':x3' , float(self.xSpline.c.item(0,i)))

            if not xQuery.exec():
                raise queryError(xQuery)
    
    #insert into x_spline table
        runQuery('delete from y_spline where mfv_number = :mfv',db = db,values = {':mfv':mfvNumber})
        yQuery = prepareQuery('insert into y_spline(mfv_number,start_m,end_m,y0,y1,y2,y3) values (:mfv,:start_m, :end_m, :y0 , :y1 ,:y2 , :y3)' , db = db)
        for i,m in enumerate(self.ySpline.x[0:-1]):
            yQuery.bindValue(':mfv' , mfvNumber)
            yQuery.bindValue(':start_m' , float(m))
            yQuery.bindValue(':end_m' , float(self.ySpline.x[i+1]))
            yQuery.bindValue(':y0' , float(self.ySpline.c.item(3,i)))
            yQuery.bindValue(':y1' , float(self.ySpline.c.item(2,i)))
            yQuery.bindValue(':y2' , float(self.ySpline.c.item(1,i)))
            yQuery.bindValue(':y3' , float(self.ySpline.c.item(0,i)))

            if not yQuery.exec():
                raise queryError(yQuery)


        db.commit()
        
        
        
    def findMO(self, pt:QgsPointXY , minM:float = 0.0 , maxM:float = dims.MAX_M) -> MO:
        m = self.nearestM(pt = pt,minM = minM,maxM = maxM)
        nearestPoint:QgsPointXY = self.point(m)
        shortestLine = (pt.x() - nearestPoint.x() , pt.y() - nearestPoint.y())#line from nearest -> point
        lp = self.leftPerp(m)
        offset = shortestLine[0] * lp[0] + shortestLine[1] * lp[1]#dot product
        return MO(m=m,offset=offset) # left is positive
        
        
    #works well for within small range
    def nearestM(self , pt:QgsPointXY , minM:float = 0.0 , maxM:float = dims.MAX_M , tol:float = 0.01) -> float:
            
        def _sqdist(m):
            return pt.distance(self.point(m))
            
        #bounds should be between self.minM and self.maxM
        lower = max(self.minM,minM)
        upper = min(self.maxM,maxM)
        
        res = minimize_scalar(_sqdist,bounds = (lower,upper),method='bounded',tol = tol)
        if res.success:
            return res.x            
        else:
            raise ValueError('Could not minimize distance')
    
    
    
    #specialized for finding nearest frame to point.
    #only used when user clicks button. speed unimportant.
    #nearestM being unreliable for large m range. numpy optimize stuck in local minimum?
    def findFrame(self,point:QgsPointXY) -> int:
        mVals = np.arange(self.minM , self.maxM , dims.HEIGHT/4)
        xDif = self.xSpline(mVals) - point.x()
        yDif = self.ySpline(mVals) - point.y()
        sqdif = xDif*xDif + yDif*yDif
        return dims.mToFrame(mVals[np.argmin(sqdif)])
        
    
    
    
    
    def framePixelLineToPoint(self,frame:int,pixel:int,line:int,chainageShift:float, offset:float) -> QgsPointXY:
        m = dims.lineToM(frame = frame,line = line) + chainageShift
        newOffset = dims.pixelToOffset(pixel) + offset
        return self.offsetPoint(m=m , offset = newOffset)
    
    
    

    def gcps(self,frame:int, chainageShift:float, offset:float) -> list[gcp]:
        r = []
        N = 3 # GCP points per side of frame
       # startM = dims.lineToM(frame,dims.LINES) + chainageShift # start of frame + shift
      #  endM = startM + dims.HEIGHT
        lines = np.linspace(start = 0,stop = dims.LINES , num = N)

        for floatLine in lines:
            line = int(floatLine)
            left = self.framePixelLineToPoint(frame = frame , pixel = 0 , line = line,chainageShift = chainageShift , offset = offset)
            g = gcp(x = left.x() ,y = left.y() , pixel = 0, line = line)
            r.append(g)
            #right edge
            right = self.framePixelLineToPoint(frame = frame , pixel = dims.PIXELS , line = line , chainageShift = chainageShift , offset = offset)
            g2 = gcp(x = right.x() ,y = right.y() , pixel = dims.PIXELS, line = line)
            r.append(g2)
        return r
       
    
    
class gpsSystem:
    __slots__ = ("curves","currentMfv")



    def __init__(self):
        self.curves: dict[str,curve|None] = {}
        self.currentMfv:str = ''
    
    
    
    #raise helpful error if curve not found
    def currentCurve(self) -> curve:
        if self.currentMfv in self.curves:
            return self.curves[self.currentMfv]
        else:
            raise KeyError('no GPS for mfv : "{mfv}"'.format(mfv = self.currentMfv))
    
    
    def crs(self):
        return settings.destCrs()
    
    def setCurve(self, mfv:str ,c:curve):
        self.curves[mfv] = c

    
    def setMfv(self,mfv:str):
        self.currentMfv = mfv
    
    
    def centerLine(self,startFrame:int,endFrame:int) -> QgsGeometry:
        points = []
        if self.currentMfv in self.curves:
            for frame in range(startFrame,endFrame+1):
                points.append(self.curves[self.currentMfv].point(dims.frameToM(frame)))
        return QgsGeometry.fromPolylineXY(points)
    
    
    def findFrame(self,pt:QgsPointXY) -> int:
        return self.currentCurve().findFrame(pt)
        
        
        
    
    def makeLayer(self):
        
        uri = "LineString?crs=epsg:{p}&field=mfv:str&field=frame:int&field=start_chain:int&field=end_chain:int&index=yes".format(p = settings.destSrid())    
        layer = QgsVectorLayer(uri,'original_GPS',"memory")
        
        fields = layer.fields()    
        
        with edit(layer):
    
            for k,v in self.curves.items():
                layer.addFeatures(v.features(fields = fields , mfv = k))
                 
        #layer.loadNamedStyle(file_locations.centerStyle)
       # load_image.loadLayer(layer)
        group = group_functions.getGroup(['image_loader'])#QgsLayerTreeGroup
        group.addLayer(layer)
    
        node = group.findLayer(layer)
        node.setItemVisibilityChecked(True)
        node.setExpanded(False)        
        QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
    
    

    @staticmethod
    def fromDatabase(db,mfvs:list[str]):
        r = gpsSystem()
        for mfv in mfvs:
            try:
                c = curve.fromDatabase(db,mfv)
                r.curves[mfv] = c
            except Exception as e:
                print(e)
                #r.curves[mfv] = None
        return r
    
    def toDatabase(self,db):
        pass
    
    
    
    
    
    
    
    
#make and load vector layer from dict of mfv_ref:curve
def makeLayer(data:dict[str,curve])-> QgsVectorLayer:
    uri = "LineString?crs=epsg:{p}&field=mfv:str&field=frame:int&field=start_chain:int&field=end_chain:int&index=yes".format(p = settings.destSrid())    
    layer = QgsVectorLayer(uri,'original_GPS',"memory")
    
    fields = layer.fields()    
    
    with edit(layer):

        for k,v in data.items():
            layer.addFeatures(v.features(fields = fields , mfv = k))
             
             
    #layer.loadNamedStyle(file_locations.centerStyle)
   # load_image.loadLayer(layer)
    group = group_functions.getGroup(['image_loader'])#QgsLayerTreeGroup
    group.addLayer(layer)

    node = group.findLayer(layer)
    node.setItemVisibilityChecked(True)
    node.setExpanded(False)        
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend













class frame(NamedTuple):
    mfv: str
    frame: int




