from PyQt5.QtSql import QSqlQuery
#from osgeo.osr import SpatialReference, CoordinateTransformation, OAMS_TRADITIONAL_GIS_ORDER
from qgis.core import QgsGeometry, QgsPointXY
import numpy as np
import csv
import os
from PyQt5.QtCore import QSettings

from image_loader.db_functions import runQuery, defaultDb, queryError, queryPrepareError
from image_loader.type_conversions import asBool

settings = QSettings("pts" , "image_loader")


# transform for parsing csv
#epsg4326 = SpatialReference()
#epsg4326.ImportFromEPSG(4326)
#epsg4326.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)
# without this some gdal versions expect y arg to TransformPoint before x.version dependent bad design.
#epsg27700 = SpatialReference()
#epsg27700.ImportFromEPSG(27700)
#transform = CoordinateTransformation(epsg4326, epsg27700)


#from pyproj import Transformer
#transformer = Transformer.from_crs(4326,27700,always_xy=True)
#def transformPoint(lon,lat):
    #return transformer.transform(lon, lat)




def parseCsv(file):
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for i, d in enumerate(reader):
            try:
                # need round to avoid floating point errors like int(1.001*1000) = 1000
                m = round(float(d['Chainage (km)'])*1000)
                lon = float(d['Longitude (deg)'])
                lat = float(d['Latitude (deg)'])
              #  x, y  = transformPoint(lon, lat)
                yield m, lon, lat
            except Exception as e:
                print(e)
                pass

class gpsInterface:
    
    @staticmethod
    def clear():
        runQuery(query='delete from original_points')


    @staticmethod
    def loadFile(file,interval = 5):
        

        
        ext = os.path.splitext(file)[1]
        if ext == '.csv':
            #gpsInterface.setValues(vals = parseCsv(file),startAtZero=startAtZero)

            d = np.array([r for r in parseCsv(file)])
            #print('data:',d)
        
        if d is not None:
            if d.size >0:
                #interpolate and resample at intervals. every 1m excessive and not smooth?
                if interval is not None:
                    
                    m = d[:,0]                    
                    lon = d[:,1]
                    lat = d[:,2]
                    
                    #start at multiple of interval after start
                    s = min(m)
                    if s%interval != 0:
                        s = s + interval - s % interval
                    
                    e = max(m)
                    if e%interval != 0:
                        e = e - e % interval        
                    
                    newM = np.arange(s,e,interval)
                    newLon = np.interp(newM, m, lon)
                    newLat = np.interp(newM, m, lat)
            
                    r = np.transpose((newM,newLon,newLat))
                else:
                    r = d
                gpsInterface.setValues(vals = r)


    @staticmethod
    def setValues(vals):
        db = defaultDb()
        db.transaction()
        runQuery(query='delete from original_points', db=db)
        q = QSqlQuery(db)
        if not q.prepare('insert or ignore into original_points(m,pt) values (cast(:m as int),makePoint(:x,:y,4326))'):
            raise queryPrepareError(q)
        for i, v in enumerate(vals):
            try:
                q.bindValue(':m', float(v[0]))
                q.bindValue(':x', float(v[1]))
                q.bindValue(':y', float(v[2]))
                if not q.exec():
                    raise queryError(q)
            except Exception as e:
                message = 'error loading row {r} : {err}'.format(r=i, err=e)
                print(message)
        startAtZero = asBool(settings.value('startAtZero'),True)
        if startAtZero:
            runQuery('update original_points set m = m - (select min(m) from original_points)', db=db)
        runQuery('update original_points set next_id = (select id from original_points as np where np.m>original_points.m order by np.m limit 1)', db=db)
        runQuery('update original_points set next_m = (select m from original_points as np where np.m>original_points.m order by np.m limit 1)', db=db)
        db.commit()
    
    
    @staticmethod    
    def maxM():
        q = runQuery('select max(m) from original_points')
        while q.next():
            return q.value(0)
        
    
    @staticmethod
  # performance unimportant here.
    def line(startM, endM, maxPoints=2000, corrected=False):
        if startM < endM:
            s = startM
            e = endM
        else:
            s = endM
            e = startM

        if corrected:
            table = 'corrected_points'
        else:
            table = 'original_points'

        q = '''select :s
                ,last.x + (st_x(next.pt)-last.x)*(:s - last.m)/(next.m-last.m)
                ,last.y + (st_y(next.pt)-last.y)*(:s - last.m)/(next.m-last.m)
                from
                (select m,st_x(pt) as x,st_y(pt) as y,next_m from {t} where m <= :s and next_m > :s) last
                inner join {t} as next on next.m = last.next_m
        union		
        select m,st_x(pt),st_y(pt) from {t} where :s<= m and m <= :e
        UNION
        select :e
                ,last.x + (st_x(next.pt)-last.x)*(:e - last.m)/(next.m-last.m)
                ,last.y + (st_y(next.pt)-last.y)*(:e - last.m)/(next.m-last.m)
                from
                (select m,st_x(pt) as x,st_y(pt) as y,next_m from {t} where m <= :e and next_m > :e) last
                inner join {t} as next on next.m = last.next_m
        order by m
        limit {maxPoints}
        '''.format(maxPoints=maxPoints,t = table)

        q = runQuery(q, values={':s': s, ':e': e})
        p = []
        while q.next():
            p.append((q.value(1), q.value(2)))

        if p:
            if startM > endM:
                p = reversed(p)
            return QgsGeometry.fromPolylineXY([QgsPointXY(i[0], i[1]) for i in p])

        return QgsGeometry()



    @staticmethod
    def tableHasGps():
        return gpsInterface.tableRowCount() > 0

    @staticmethod
    def tableRowCount():
        q = runQuery('select count(m) from original_points')
        while q.next():
            return q.value(0)