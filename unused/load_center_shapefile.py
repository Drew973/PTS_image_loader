# -*- coding: utf-8 -*-
"""
Created on Thu Sep 14 13:56:54 2023

@author: Drew.Bennett
"""


from osgeo import ogr
from osgeo import osr

from PyQt5.QtSql import QSqlQuery
from image_loader.db_functions import defaultDb,queryPrepareError,queryError,runQuery

#(id,x,y)
def parseShapefile(file):
    OutSR = osr.SpatialReference()
    OutSR.ImportFromEPSG(27700)
    shapefile = ogr.Open(file)
    part = 1
    layer = shapefile.GetLayer()
    for feature in layer:
        geom = feature.GetGeometryRef()
        geom.TransformTo(OutSR)
        for i in range(0, geom.GetPointCount()):
            pt = geom.GetPoint(i)#tuple
            yield (part,pt[0], pt[1])
            part +=1

def testParse():            
    file = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\1_007_centerline\2023-01-21 10h08m11s GPS MFV1_007(Polyline).shp'
    for r in parseShapefile(file):
        print(r)
        
        
        
        
def loadShapefile(file):
    db = defaultDb()
    db.transaction()
    runQuery('delete from original_points',db=db)
    
    
    q = QSqlQuery(db)
    if not q.prepare('insert into original_points(id,pt) values (:id,MakePoint(:x,:y,27700))'):
        raise queryPrepareError(q)
        
    for r in parseShapefile(file):
        q.bindValue(':id',r[0])
        q.bindValue(':x',r[1])
        q.bindValue(':y',r[2])
    
        if not q.exec():
            print(q.boundValues())
            raise queryError(q)
            
            
    updateQuery = 'update original_points set m = coalesce((select new_m from (select id,sum(st_distance(pt,(select pt from original_points as np where np.id = original_points.id -1 ))) over (order by id) as new_m from original_points)a where a.id = original_points.id),0)'
    runQuery(updateQuery,db=db)
    runQuery('update original_points set next_id = id+1',db=db)

    runQuery(db=db,query='delete from corrected_points')
    runQuery(db=db,query='insert into corrected_points(m,pt) select m,pt from original_points')
    runQuery('update corrected_points set next_id = id+1',db=db)

    db.commit()
        
        
def testLoad():
    file = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\1_007_centerline\2023-01-21 10h08m11s GPS MFV1_007(Polyline).shp'
    loadShapefile(file)
        
if __name__ == '__console__':
    testLoad()