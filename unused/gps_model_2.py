# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:38:29 2023

@author: Drew.Bennett

can do without saving gps points.
do gps in seperate database.
gps_model should be for handling geometries.


"""
from collections import namedtuple
import csv
import os
from image_loader.trajectory import trajectory
from osgeo.osr import SpatialReference, CoordinateTransformation,OAMS_TRADITIONAL_GIS_ORDER
import numpy as np
from qgis.core import QgsPointXY,QgsGeometry
from image_loader.dims import WIDTH,LINES,PIXELS,HEIGHT


epsg4326 = SpatialReference()
epsg4326.ImportFromEPSG(4326)
epsg4326.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)
#version dependent bad design.
#without this some gdal versions expect y arg to TransformPoint before x

epsg27700 = SpatialReference()
epsg27700.ImportFromEPSG(27700)
transform = CoordinateTransformation(epsg4326,epsg27700)

W = 2.5


mxy = namedtuple("mxy", ['m','x','y'])


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

#need frame arg to distinguish end from start of next frame
def mToLine(m,frame):
    if np.isfinite(m):
        startM = (frame-1)*HEIGHT
        endM = frame*HEIGHT
        if m<startM:
            return LINES
        if m>endM:
            return 0
        return round(LINES - LINES*(m-startM)/HEIGHT)
    return 0
    
#float/np float -> int
def offsetToPixel(offset):
    if np.isfinite(offset):
        return round(PIXELS * 0.5 - offset * PIXELS / WIDTH )
    return 0


def finite(a):
    return np.all(np.isfinite(a))


def toQgsPointXY(a):
    if finite(a):
        return QgsPointXY(a[0],a[1])
    return QgsPointXY()


#[[x,y],[x2,y2]]
def toArray(points):
    return np.array([[p.x(),p.y()] for p in points])


class gpsModel:
    
    def __init__(self):
        self.clear()

       
    def clear(self):
        self.original = trajectory()
        self.corrected = trajectory()


    @staticmethod
    def lineToM(frame,line):
        return HEIGHT * (frame-line/LINES)


    @staticmethod
    def pixelToOffset(pixel):
        return WIDTH*0.5-pixel*WIDTH/PIXELS


    def loadFile(self,file):
        ext = os.path.splitext(file)[1]
        if ext == '.csv':
            self.original.setValues(parseCsv(file))
            self.setCorrections(None)
            print(self.original.values()[0:10])
            
        
    #-> QgsPointXY
    def originalPoints(self,m):
        self.original
    
    
    #def hasGps() -> bool
    def hasGps(self):
        return self.original.count()>0
    
    
    #performance unimportant here ~0.5s fine
    #-> (m,offset)
    def locatePointOriginal(self,point,minM = 0,maxM = np.inf):
        p = np.array([point.x(),point.y()])
        return self.original.locatePoint(p)


    #performance unimportant here ~0.5s fine
    #-> (m,offset)
    def locatePointCorrected(self,point,minM = 0,maxM = np.inf):
        p = np.array([point.x(),point.y()])
        return self.corrected.locatePoint(p,minM=minM,maxM=maxM)
    
    
    def originalPoint(self,m,offset):       
        return toQgsPointXY(self.original.point(m,offset))
       
        
    def correctedPoint(self,m,offset):       
        return toQgsPointXY(self.corrected.point(m,offset))


    #find original offset of point pt
    def offset(self,m,point):
        p = toArray([point])
        m = np.array([m],dtype = np.double)
        return self.original.findOffsets(m,p)[0]


#array [m,offset]
    def correctedPoints(self,mo):
        return [toQgsPointXY(row) for row in self.original.offsetPoints(mo)]


    def getFrame(self,point):
        m,offset = self.locatePointOriginal(point)[0]
        if np.isfinite(m):
            return int(np.ceil(m/HEIGHT))
        else:
            return -1
    
    
    #->(pixel,line)
    def getPixelLine(self,point,frameId):
        m,offset = self.locatePointCorrected(point,minM = frameId*HEIGHT,maxM=(frameId+1)*HEIGHT)[0]
      #  print('m',m,'offset',offset)
        return (offsetToPixel(offset),mToLine(m,frameId))
    
    
    #performance unimportant.
    #pt:QgsPointXY ->(m float,offset float)
    def correctedM(points):
        pass
    
    
    #performance unimportant.
    def originalLine(self,startM,endM,maxPoints = 2000):
        if startM < endM:
            p = self.original.line(startM,endM,maxPoints = 2000)
            return QgsGeometry.fromPolylineXY([QgsPointXY(i[1],i[2]) for i in p])
        if startM > endM:
            p = self.original.line(endM,startM,maxPoints = 2000)
            return QgsGeometry.fromPolylineXY(reversed([QgsPointXY(i[1],i[2]) for i in p]))
        return QgsGeometry()


    ############################problem here
    def setCorrections(self,corrections):
       # print('corrections',corrections)
        if corrections is not None:
            vals = self.original.values()
            mShifts = np.interp(x = vals['m'],xp = corrections['m'],fp = corrections['m_shift'])
           
            mxyType = [('m',np.double),('x',np.double),('y',np.double)]
            newVals = np.empty(vals.shape,dtype = mxyType)
            newVals['m'] = vals['m'] + mShifts
            
            moType = [('m',np.double),('offset',np.double)]
            mo = np.empty(vals.shape, dtype=moType)
            mo['m'] = vals['m']
            mo['offset'] = np.interp(x = vals['m'],xp = corrections['m'],fp = corrections['offset_shift'])
            
            newVals[['x','y']] = self.original.offsetPoints(mo)#x,y
            print('newVals',newVals)
            self.corrected.setValues(newVals)
        else:
            self.corrected.setValues(self.original.values())
    
    
    #[(x,y,pixel,line)]
    def gcps(self,frame):
        r = []
        s = HEIGHT * (frame - 1)
        m = np.linspace(s, s+HEIGHT, num=5)
        
        leftOffsets = m * 0 + WIDTH/2
        rightOffsets = m * 0 - WIDTH/2

        lefts = np.transpose(np.row_stack([m,leftOffsets]))#m,offset
   #     print('lefts',lefts)
        xy = self.corrected.offsetPoints(lefts)
  #      print('gcp xy:',xy)

        for i,row in enumerate(xy):
            if finite(row):
                r.append((row[0],row[1],0,mToLine(m[i],frame=frame)))
                
        rights = np.transpose(np.row_stack([m,rightOffsets]))
        xy = self.corrected.offsetPoints(rights)
      #  print('gcp xy:',xy)
        for i,row in enumerate(xy):
            if finite(row):
                r.append((row[0],row[1],PIXELS,mToLine(m[i],frame=frame)))
    #    print('gcps:',r)
        return r
    
    
def testParse():
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\MFV1_007-rutacd-1.csv'
    for r in parseCsv(f):
        print(r)


def testLoadFile():
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\MFV1_007-rutacd-1.csv'
    m = gpsModel()
    m.loadFile(f)
    
    
if __name__ in ('__main__','__console__'):
    #testParse()
    
    m = gpsModel()
   # print(m)
    testLoadFile()
    
    

    