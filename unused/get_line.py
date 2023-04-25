# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 14:18:17 2023

@author: Drew.Bennett
"""


from qgis.core import QgsProject,QgsFeatureRequest,QgsCoordinateReferenceSystem,QgsGeometry

def getLine(lineLayer,startField,endField,startM,endM):
    context = QgsProject.instance().transformContext()

    #order by startField
    vertices = []
    exp = '"{sField}" <= {end} and "{eField}">= {start}'.format(sField = startField,eField=endField,end = endM,start=startM)
    req = QgsFeatureRequest().setFilterExpression(exp)
    req = req.setDestinationCrs(QgsCoordinateReferenceSystem(27700),context)
    req = req.addOrderBy(startField)

    #print(exp)

    for feat in lineLayer.getFeatures(req):
        s = feat[startField]
        e = feat[endField]
        g = feat.geometry()
      #  print(g)
        
        if s<=startM:
            frac = (startM-s)/abs(e-s)
            p = g.interpolate(frac*g.length())
            vertices.append(g.interpolate(frac*g.length()).asPoint())
    
    
        if startM<s and e< endM:
            p = g.interpolate(0)
            vertices.append(p.asPoint())
    
    
        if e>=endM:
            frac = (endM-s)/abs(e-s)
            p = g.interpolate(frac*g.length())
            vertices.append(g.interpolate(frac*g.length()).asPoint())
    
    
   # print(vertices)
    return QgsGeometry.fromPolylineXY(vertices)
    




def testGetLine():
    
    gps = QgsProject.instance().mapLayersByName('gps')
    assert len(gps)>0
    gps = gps[0]
        
    sField = 'startM'
    eField = 'endM'

    r = getLine(gps,sField,eField,500,600)
    print(r)












if __name__ == '__console__':
    testGetLine()