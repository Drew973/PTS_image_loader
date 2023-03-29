# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 15:37:31 2023

@author: Drew.Bennett
"""

from qgis.core import QgsFeatureRequest,QgsProject,QgsGeometry,QgsPointXY,QgsCoordinateReferenceSystem
import math


#gets point from point layer and m value.
#field = field with m values.


#def measureToPoint(layer:QgsVectorLayer,field:str,m:float): -> QgsPointXY
def measureToPoint(layer,field,m):
      
        context = QgsProject.instance().transformContext()
        
        s = None
        exp = '"{f}" <= {m}'.format(f=field,m=m)
        req = QgsFeatureRequest().setFilterExpression(exp).setLimit(1).addOrderBy('"{f}"'.format(f = field), ascending = False)
        req = req.setDestinationCrs(QgsCoordinateReferenceSystem(27700),context)
        sp = QgsPointXY()
        for f in layer.getFeatures(req):
            sp = f.geometry().asPoint()
            s = f[field]
        
       
        exp = '"{f}" >= {m}'.format(f=field,m=m)
        req = QgsFeatureRequest().setFilterExpression(exp).setLimit(1).addOrderBy('"{f}"'.format(f = field), ascending = True)
        req = req.setDestinationCrs(QgsCoordinateReferenceSystem(27700),context)

        e = None
        ep = QgsPointXY()
        for f in layer.getFeatures(req):
            ep = f.geometry().asPoint()
            e = f[field]
        
        
        #print('s',s,'e',e)
        
        if s is None and e is None:
            return  QgsPointXY()
        
        if s and e is None:
            return sp
        
        if e and s is None:
            return ep
    
        if s==e:
            return sp
        else:
            geom = QgsGeometry.fromPolylineXY([sp,ep])
            f = (m-s)/(e-s)
            p = geom.interpolate(f * geom.length())
            if not p.isNull():
                return p.asPoint()
        
        return QgsPointXY()
        
    
    
    
    
    
#def measureToPoint(layer:QgsVectorLayer,field:str,m:float[]): -> QgsPointXY[]
def measuresToPoints(layer,startField,endField,measures):
      
        context = QgsProject.instance().transformContext()
        
        exp = '"{sField}"<= "{maximum}" and "{eField}" >= {minimum}'.format(sField = startField,eField=endField,maximum = max(measures),minimum = min(measures))
        req = QgsFeatureRequest().setFilterExpression(exp)
        req = req.setDestinationCrs(QgsCoordinateReferenceSystem(27700),context)
        
        for f in layer.getFeatures(req):
            s = f[startField]
            e = f[endField]
            
            #for m in measures:
            #    pass
     
    
    
    
    

def testMeasureToPoint():
    
    points = QgsProject.instance().mapLayersByName('points')
    assert len(points)>0
    points = points[0]
        
        
    field = 'Chainage (km)'
    
    r = measureToPoint(points,field,0.101)
    print(r)
    
    r = measureToPoint(points,field,5013.5)
  #  print(r)


    r = measureToPoint(points,field,0)
   # print(r)

    r = measureToPoint(points,field,100000)
    #print(r)
    
if __name__ in ('__console__'):
    testMeasureToPoint()
