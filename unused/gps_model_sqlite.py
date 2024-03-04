# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 09:26:59 2023

@author: Drew.Bennett


class for mapping chainage+offset to x,y

offset means multiple (x,y) per (chainage,offset) where vertex is closest point.

initial/uncorrected position has no offset.

corrections as chainage/offset vs x,y shift?
increasing offset correction can stretch/compress image...
so can multiple x,y shift.


image_id ->
chainages -> 

originalCenterline -> 
corrected_centerline->
    offset either side.
GCPs

    


m to point:
    get  get nearest 3 points   
    
point to M:
    get nearest 3 points
    linelocatePoint
    interpolate m
    offset  = dotProduct(shortestLine,vect)
    if m is on vertex then distance 
    
"""

import csv
from pyproj import Transformer
import sqlite3


class gpsModel:
    
    def __init__(self,file = ':memory:'):
        connection = sqlite3.connect(r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\test.db')
        self.con = connection
        cursor = self.con.cursor()
        q = '''
        BEGIN;

        create table if not exists points(
            pk INTEGER PRIMARY KEY
            ,m float not null unique
            ,x float
            ,y float
            ,next_pk bigint
            ,last_pk bigint
            );

        CREATE INDEX IF NOT EXISTS m_index on points(m);
        COMMIT;
        '''
        cursor.executescript(q)
        #corrected_m float#do in view?
        cursor.close()
        
        
    def clear(self):
        self.con.cursor().execute('delete from points')
        
        
    def release(self):
        self.con.close()
        
        
    def loadCsv(self,file):
        cur = self.con.cursor()
        cur.executemany("INSERT INTO points(m,x,y) VALUES(?, ?, ?)", parseGps(file))
        s = '''with a as (
                select pk,lead(pk) over (order by m) as next from points
                )
                update points set next_pk = next from a where a.pk = points.pk;
                
              with a as (
              select pk,lead(pk) over (order by m desc) as last from points
              )
              update points set last_pk = last from a where a.pk = points.pk;
        '''
        cur.executescript(s)
        self.con.commit() 
               
    
    def getPoint(self,m,offset):
        pass
    
    
    def getM(self,pt,run=''):
        pass
    
    
    
transformer = Transformer.from_crs("EPSG:4326", "EPSG:27700")    
def parseGps(file):
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        for i,d in enumerate(reader):
            pt = transformer.transform(float(d['Longitude (deg)']),float(d['Latitude (deg)']))
            yield (float(d['Chainage (km)'])*1000,#m
                   pt[0],#x
                   pt[1])#y
    
    


#f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\test.db'

#m = gpsModel(f)
#m.release()
#del m
# define connection and cursor
#connection = sqlite3.connect(f)
##cursor = connection.cursor()
 
# create the user defined function
#connection.create_function("ROHACK", 2, _customFun)
