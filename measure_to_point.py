# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 15:37:31 2023

@author: Drew.Bennett
"""

from qgis.core import QgsFeatureRequest,QgsProject,QgsPointXY,QgsCoordinateReferenceSystem




def measureToPoint(layer,startField,endField,m):
    
    context = QgsProject.instance().transformContext()

    exp = '"{sField}" <= {v} and {v} <= "{eField}"'.format(sField = startField,eField=endField,v = m)
  #  print(exp)
    req = QgsFeatureRequest().setFilterExpression(exp)
    req = req.setDestinationCrs(QgsCoordinateReferenceSystem(27700),context)
 #   req.setLimit(1)
    
    for f in layer.getFeatures(req):
        try:
            s = float(f[startField])
            e = float(f[endField])
            geom = f.geometry()
            frac = (m-s)/abs(e-s)
            #print('frac',frac)
            p = geom.interpolate(frac*geom.length())
            return p.asPoint()
        except Exception as e:
            print(e.__repr__())
    
    return QgsPointXY()
    
    
    
#def measureToPoint(layer:QgsVectorLayer,field:str,m:float[]): -> QgsPointXY[]
def measuresToPoints(layer,startField,endField,measures):
      
    context = QgsProject.instance().transformContext()
    points = [QgsPointXY()]*len(measures)
        
    for i,m in enumerate(measures):
        exp = '"{sField}" <= {v} and {v} <= "{eField}"'.format(sField = startField,eField=endField,v = m)
      #  print(exp)
        req = QgsFeatureRequest().setFilterExpression(exp)
        req = req.setDestinationCrs(QgsCoordinateReferenceSystem(27700),context)
        req.setLimit(1)
        
        for f in layer.getFeatures(req):
            try:
                s = float(f[startField])
                e = float(f[endField])
                geom = f.geometry()
                frac = (m-s)/abs(e-s)
                #print('frac',frac)
                p = geom.interpolate(frac*geom.length())
                points[i] = p.asPoint()
            except Exception as e:
                print(e.__repr__())
            break#*should* only have 1 feature as limit set.   
    return points
    
    

    
def testMeasuresToPoint():
    
    gps = QgsProject.instance().mapLayersByName('gps')
    assert len(gps)>0
    gps = gps[0]
        
    sField = 'start_m'
    eField = 'end_m'

    r = measuresToPoints(gps,sField,eField,[1,2,3,4,5,6,7,8,9])
    print(r)
    
    
    
def testMeasureToPoint():
    
    gps = QgsProject.instance().mapLayersByName('gps')
    assert len(gps)>0
    gps = gps[0]
        
    sField = 'start_m'
    eField = 'end_m'

    r = measureToPoint(gps,sField,eField,9)
    print(r)
        
    
    
if __name__ in ('__console__'):
  #  testMeasuresToPoint()
    testMeasureToPoint()