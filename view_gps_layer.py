# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 10:46:12 2023

@author: Drew.Bennett
"""

from qgis.core import QgsFeature,QgsGeometry,QgsPointXY,edit
from qgis.utils import iface

from image_loader import db_functions



def loadGpsLayer():

    uri = "PointM?crs=epsg:27700&field=chainage:double&index=yes"
    name = 'GPS'
    layer = iface.addVectorLayer(uri, name, "memory")
    fields = layer.fields()
    
    def features():
        q = db_functions.runQuery(query = 'select m,corrected_x,corrected_y from points')
        while q.next():
            f = QgsFeature(fields)
            f['chainage'] = q.value(0)
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(q.value(1),q.value(2))))
            yield f
    
    
    with edit(layer):
         layer.addFeatures(features())
         

if __name__ == '__console__':
    loadGpsLayer()