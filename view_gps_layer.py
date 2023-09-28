# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 10:46:12 2023

@author: Drew.Bennett
"""

from qgis.core import QgsFeature,QgsGeometry,edit
from qgis.utils import iface

from image_loader import db_functions




def loadGpsLines(corrected = True):
    uri = "Linestring?crs=epsg:27700&field=id:int&field=start_m:real&field=end_m:real&index=yes"
    if corrected:
        name = 'corrected_GPS'
    else:
        name = 'uncorrected_GPS'
    layer = iface.addVectorLayer(uri, name, "memory")
    fields = layer.fields()
    def features():
        if corrected:
            q = db_functions.runQuery(query = 'select id,start_m,end_m,st_asText(line) from corrected_lines')
        else:
            q = db_functions.runQuery(query = 'select id,start_m,end_m,st_asText(line) from lines')
        while q.next():
            f = QgsFeature(fields)
            f['id'] = q.value(0)
            f['start_m'] = q.value(1)
            f['end_m'] = q.value(2)
            f.setGeometry(QgsGeometry.fromWkt(q.value(3)))
            yield f
    with edit(layer):
         layer.addFeatures(features())


if __name__ == '__console__':
    loadGpsLines()