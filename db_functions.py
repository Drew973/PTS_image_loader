# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 14:28:37 2023

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlDatabase,QSqlQuery


class queryError(Exception):
    def __init__(self,query):
        super().__init__('error executing query {q}:{err}'.format(q = query.lastQuery(),err = query.lastError().text()))



def initDb(db):
    db.transaction()
    
    r = db.exec('''create table if not exists gps 
            ( m INTEGER NOT NULL PRIMARY KEY,
             x float,
             y float
        )''')
            
    if not r:
        raise queryError(r)
            
            
    db.commit()
    
    
import csv
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject,QgsPoint


def loadGps(db,file):
    
    db.transaction()
    r = db.exec('delete from gps')
    if not r:
        raise queryError(r)


    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),
        QgsCoordinateReferenceSystem('EPSG:27700'),
        QgsProject.instance())    
    
    q = QSqlQuery(db)
    if not q.prepare('insert into gps(m,x,y) values(:m,:x,:y)'):
        raise queryError(q)
    
    with open(file,'r') as f:
        reader = csv.DictReader(f)
        
        for i,d in enumerate(reader):
            x = float(d['Longitude (deg)'])
            y = float(d['Latitude (deg)'])
            pt = transform.transform(x,y)
            m = round(float(d['Chainage (km)'])*1000)#nearest int. floating point problems if don't round.
            q.bindValue(':m',m)
            q.bindValue(':x',pt.x())
            q.bindValue(':y',pt.y())

            if not q.exec():
                print(q.boundValues())
                raise queryError(q)
   # print(a[990:1010])
    #print(values[990:1010])
    db.commit()




def getLine(db,start,end):
    q = 'select m,x,y from gps where {start} <=m and m<= {end} order by m'.format(start=start-1,end=end+1)
    
    #gps at 1m intervals. want values either side.
    
    query = db.exec(q)
    points = []
    
    
    while query.next():
        #print(query.value(0),query.value(1),query.value(2))
        points.append(QgsPoint( m = query.value(0), x = query.value(1),y = query.value(2) ))
    
    print(points)
    
    if len(points)<2:#need at least 2 points for line.
        return

    


import os
    
db = QSqlDatabase.addDatabase("QSQLITE",'image_loader')
dbFile = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\images.db'

db.setDatabaseName(dbFile)
if not db.open():
    raise ValueError('could not open database')


def test():

    initDb(db)

    folder = r'D:\RAF Shawbury\Hawkeye Exported Data'
    file = os.path.join(folder,'MFV1_021-rutacd-1.csv')

    loadGps(db,file)

    getLine(db,10,20)

    db.close()
    
    
if __name__ =='__console__':
    test()
