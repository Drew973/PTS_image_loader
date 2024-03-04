# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 10:46:12 2023

@author: Drew.Bennett
"""

from qgis.core import QgsFeature,QgsGeometry,edit
from qgis.utils import iface
from image_loader import db_functions
from image_loader.layer_styles.styles import centerStyle



def loadGps(corrected = False):
    uri = "LineString?crs=epsg:27700&field=run:int&field=frame:int&field=start_chain:int&field=end_chain:int&index=yes"
    if corrected:
        name = 'corrected_GPS'
    else:
        name = 'original_GPS'
    layer = iface.addVectorLayer(uri, name, "memory")
    fields = layer.fields()
        
    def features():
        q = db_functions.runQuery(query = 'select number,frame,start_m,end_m,st_asText(geom) from lines_5m left join runs_view on frame>= start_frame and frame <= end_frame')
        while q.next():
            f = QgsFeature(fields)
            f['run'] = q.value(0)
            f['frame'] = q.value(1)
            f['start_chain'] = q.value(2)
            f['end_chain'] = q.value(3)
            f.setGeometry(QgsGeometry.fromWkt(str(q.value(4))))
            if f.isValid():
                yield f
                
    with edit(layer):
         layer.addFeatures(features())
    layer.loadNamedStyle(centerStyle)





if __name__ == '__console__':
    loadGps()