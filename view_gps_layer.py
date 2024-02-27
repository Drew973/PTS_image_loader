# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 10:46:12 2023

@author: Drew.Bennett
"""

from qgis.core import QgsFeature,QgsGeometry,edit,QgsPointXY
from qgis.utils import iface
from image_loader import db_functions
from image_loader.layer_styles.styles import centerStyle


def _loadGps(corrected = True):
    uri = "Point?crs=epsg:27700&field=id:int&field=m:real&index=yes"
    if corrected:
        name = 'corrected_GPS'
    else:
        name = 'uncorrected_GPS'
    layer = iface.addVectorLayer(uri, name, "memory")
    fields = layer.fields()
    def features():
        if corrected:
            q = db_functions.runQuery(query = 'select id,m,st_x(pt),st_y(pt) from corrected_points')
        else:
            q = db_functions.runQuery(query = 'select id,m,st_x(pt),st_y(pt) from original_points')
        while q.next():
            f = QgsFeature(fields)
            f['id'] = q.value(0)
            f['m'] = q.value(1)
            
            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(q.value(2),q.value(3))))
            yield f
    with edit(layer):
         layer.addFeatures(features())





def loadGps(corrected = False):
    uri = "LineString?crs=epsg:27700&field=frame:int&field=start_chain:int&field=end_chain:int&index=yes"
    if corrected:
        name = 'corrected_GPS'
    else:
        name = 'original_GPS'
    layer = iface.addVectorLayer(uri, name, "memory")
    fields = layer.fields()
        
    def features():
        q = db_functions.runQuery(query = 'select frame,start_m,end_m,st_asText(geom) from lines_5m')
        while q.next():
            f = QgsFeature(fields)
            f['frame'] = q.value(0)
            f['start_chain'] = q.value(1)
            f['end_chain'] = q.value(2)
            f.setGeometry(QgsGeometry.fromWkt(str(q.value(3))))
            if f.isValid():
                yield f
                
    with edit(layer):
         layer.addFeatures(features())
    layer.loadNamedStyle(centerStyle)





if __name__ == '__console__':
    loadGps()