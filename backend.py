# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 11:59:35 2024

@author: Drew.Bennett


start moving everything database specific to here.

make as procedural as possible for easier testing. database state for testing?

"""

import numpy as np
import csv
import math
from PyQt5.QtSql import QSqlQuery
from image_loader.splinestring import splineString
from image_loader import settings,dims
from image_loader.db_functions import runQuery, defaultDb, queryError, queryPrepareError , prepareQuery
from image_loader.type_conversions import asBool


#ESPG:4326
#meant for rutacd csvs. 1m intervals
def parseCsv(file : str , interval = 5):
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for i , d in enumerate(reader):
            try:
                # need round to avoid floating point errors like int(1.001*1000) = 1000
                m : int = round(float(d['Chainage (km)'])*1000)
                lon = float(d['Longitude (deg)'])
                lat = float(d['Latitude (deg)'])
                alt = float(d['Altitude (m)'])
                if m % interval == 0:
                    yield ( m , lon , lat , alt )
            except Exception as e:
                print(e)
                pass


#numpy array
def setValues(vals):
    db = defaultDb()
    db.transaction()
    runQuery(query='delete from original_points', db=db)
    q = QSqlQuery(db)
    if not q.prepare('insert or ignore into original_points(m,pt) values (cast(:m as int),MakePointZ(:x,:y,:alt,4326))'):
        raise queryPrepareError(q)
    for i, v in enumerate(vals):
        try:
            q.bindValue(':m', int(v[0]))
            q.bindValue(':x', float(v[1]))
            q.bindValue(':y', float(v[2]))
            q.bindValue(':alt', float(v[3]))
            if not q.exec():
                raise queryError(q)
        except Exception as e:
            message = 'error loading row {r} : {err}'.format(r=i, err=e)
            print(message)
    #updating points
    if asBool(settings.value('startAtZero'),True):
        runQuery('update original_points set m = m - (select min(m) from original_points)', db=db)
   # runQuery('update original_points set next_id = (select id from original_points as np where np.m>original_points.m order by np.m limit 1)', db=db)
  #  runQuery('update original_points set next_m = (select m from original_points as np where np.m>original_points.m order by np.m limit 1)', db=db)
  #  runQuery('update original_points set last_id = (select id from original_points as np where np.m<original_points.m order by np.m desc limit 1)',db=db)
    runQuery('update original_points set bearing = (select 360*atan(st_x(next.pt)-st_x(a.pt))/(st_y(next.pt)-st_y(a.pt))/6.283185307179586 from original_points as next where a.next_id = next.id ) from original_points as a' , db=db)
    runQuery('update original_points set bearing = bearing + 360 where bearing < 0' , db=db)

    #add rows to frames table
    runQuery(query='delete from frames', db=db)
    q = prepareQuery('insert into frames(id) values (:frame)' , db = db)
    numberOfFrames = math.floor((np.max(vals[:,0]) - np.min(vals[:,0]))/dims.HEIGHT)
    for frame in range(0,numberOfFrames+1):
        q.bindValue(':frame',frame)
        q.exec()
    db.commit()
        

def maxM() -> int:
    q = runQuery('select max(m) from original_points')
    while q.next():
        return q.value(0)
    
 
def minM() -> int:
    q = runQuery('select min(m) from original_points')
    while q.next():
        return q.value(0)
    return 0

def clear():
    runQuery(query='delete from original_points')
    runQuery(query='delete from frames')



def getSplineString(srid) -> splineString:
    return splineString(values = getPoints(srid))


#array [(m1,x1,y1)...]    
#spatialite reprojection ~1.5m from QGIS reprojection
#reproject in QGIS?
#~0.15s
def getPoints(srid):
    q = runQuery('select m , st_x(ST_Transform(pt,:s)) , st_y(ST_Transform(pt,:s)) from original_points order by m',
                 values = {':s' : srid},
                 forwardOnly = True)
    mxy = []
    while q.next():
        try:
            mxy.append( [ float(q.value(0)) , float(q.value(1)) , float(q.value(2)) ] )
        except Exception as e:
            pass
    return np.array(mxy,dtype = float)
  
    
  
    
  
    
