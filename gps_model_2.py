# -*- coding: utf-8 -*-
"""
Created on Tue Oct 24 11:38:29 2023

@author: Drew.Bennett

can do without saving gps points.
do gps in seperate database.
gps_model should be for handling geometries.


"""

import csv
import os
from image_loader.trajectory import trajectory
from osgeo.osr import SpatialReference, CoordinateTransformation,OAMS_TRADITIONAL_GIS_ORDER
import numpy
 

from qgis.core import QgsPointXY,QgsGeometry


epsg4326 = SpatialReference()
epsg4326.ImportFromEPSG(4326)
epsg4326.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)
#version dependent bad design.
#without this some gdal versions expect y arg to TransformPoint before x

epsg27700 = SpatialReference()
epsg27700.ImportFromEPSG(27700)
transform = CoordinateTransformation(epsg4326,epsg27700)

W = 2.5

def parseCsv(file):
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        for i,d in enumerate(reader):
            try:
                m = round(float(d['Chainage (km)'])*1000)# need round to avoid floating point errors like int(1.001*1000) = 1000
                lon = float(d['Longitude (deg)'])
                lat = float(d['Latitude (deg)'])
                x,y,z = transform.TransformPoint(lon,lat)
                yield (m,x,y)
                
            except:
                pass



WIDTH = 4.0
PIXELS = 1038
LINES = 1250
HEIGHT = 5.0

#need frame arg to distinguish end from start of next frame
def mToLine(m,frame):
    if numpy.isfinite(m):
        startM = (frame-1)*HEIGHT
        endM = frame*HEIGHT
        if m<startM:
            return LINES
        if m>endM:
            return 0
        return round(LINES - LINES*(m-startM)/HEIGHT)
    return 0
    
#float/numpy float -> int
def offsetToPixel(offset):
    if numpy.isfinite(offset):
        return round(PIXELS * 0.5 - offset * PIXELS / WIDTH )
    return 0


def finite(a):
    return numpy.all(numpy.isfinite(a))


def toQgsPointXY(a):
    if finite(a):
        return QgsPointXY(a[0],a[1])
    return QgsPointXY()


class gpsModel:
    
    def __init__(self):
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
            self.corrected.setValues(self.original.values())#should be same to start with.
       
        
    #-> QgsPointXY
    def originalPoints(self,m):
        self.original
    
    
    #def hasGps() -> bool
    def hasGps(self):
        return self.original.count()>0
    
    
    #performance unimportant here ~0.5s fine
    #-> (m,offset)
    def locatePointOriginal(self,point,minM = 0,maxM = numpy.inf):
        p = numpy.array([point.x(),point.y()])
        return self.original.locatePoint(p)


    #performance unimportant here ~0.5s fine
    #-> (m,offset)
    def locatePointCorrected(self,point,minM = 0,maxM = numpy.inf):
        p = numpy.array([point.x(),point.y()])
        return self.corrected.locatePoint(p,minM=minM,maxM=maxM)
    
    
    def originalPoint(self,m,offset):       
        return toQgsPointXY(self.original.point(m,offset))
       
        
    def correctedPoint(self,m,offset):       
        return toQgsPointXY(self.corrected.point(m,offset))

        
    def getFrame(self,point):
        m,offset = self.locatePointOriginal(point)
        if numpy.isfinite(m):
            return int(numpy.ceil(m/HEIGHT))
        else:
            return -1
    
    
    #->(pixel,line)
    def getPixelLine(self,point,frameId):
        m,offset = self.locatePointCorrected(point,minM = frameId*HEIGHT,maxM=(frameId+1)*HEIGHT)
        print('m',m,'offset',offset)
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
    
    

    