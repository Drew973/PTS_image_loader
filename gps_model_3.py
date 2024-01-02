# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 14:44:42 2023

@author: Drew.Bennett

rectangular images

"""

import csv
import os
import numpy as np
from qgis.core import QgsGeometry, QgsPointXY
# from PyQt5.QtCore import pyqtSignal

from PyQt5.QtSql import QSqlQuery
from osgeo.osr import SpatialReference, CoordinateTransformation, OAMS_TRADITIONAL_GIS_ORDER
from image_loader.db_functions import runQuery, defaultDb, queryError, queryPrepareError,prepareQuery
from image_loader.dims import HEIGHT, offsetToPixel, mToLine,lineToM,pixelToOffset,WIDTH,LINES,PIXELS,frameToM,mToFrame
from image_loader.geometry_functions import locatePoint
from scipy.interpolate import LinearNDInterpolator
from image_loader.transforms import trs,applyTranslation


def normalizeRows(a):
    s = a*a
    rowSums = np.sqrt(s.sum(axis=1))
    return a / rowSums[:, np.newaxis]

W = 0.1
maxM = 9999999999999999.9


# transform for parsing csv
epsg4326 = SpatialReference()
epsg4326.ImportFromEPSG(4326)
epsg4326.SetAxisMappingStrategy(OAMS_TRADITIONAL_GIS_ORDER)
# without this some gdal versions expect y arg to TransformPoint before x.version dependent bad design.
epsg27700 = SpatialReference()
epsg27700.ImportFromEPSG(27700)
transform = CoordinateTransformation(epsg4326, epsg27700)


def parseCsv(file):
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for i, d in enumerate(reader):
            try:
                # need round to avoid floating point errors like int(1.001*1000) = 1000
                m = round(float(d['Chainage (km)'])*1000)
                lon = float(d['Longitude (deg)'])
                lat = float(d['Latitude (deg)'])
                x, y, z = transform.TransformPoint(lon, lat)
                yield m, x, y
            except:
                pass
            
            
            
from scipy.interpolate import UnivariateSpline

correctionsK = 1#linear


class gpsModel:

    # chainageRangeChanged = pyqtSignal()


    @staticmethod
    def clear():
        runQuery(query='delete from original_points')


    @staticmethod
    def loadFile(file):
        ext = os.path.splitext(file)[1]
        if ext == '.csv':
            gpsModel.setValues(parseCsv(file))


    @staticmethod
    def setValues(vals):
        db = defaultDb()
        db.transaction()
        runQuery(query='delete from original_points', db=db)
        q = QSqlQuery(db)
        if not q.prepare('insert into original_points(m,pt) values (:m,makePoint(:x,:y,27700))'):
            raise queryPrepareError(q)
        for i, v in enumerate(vals):
            try:
                q.bindValue(':m', v[0])
                q.bindValue(':x', v[1])
                q.bindValue(':y', v[2])
                if not q.exec():
                    raise queryError(q)
            except Exception as e:
                message = 'error loading row {r} : {err}'.format(r=i, err=e)
                print(message)
        runQuery('update original_points set next_id = (select id from original_points as np where np.m>original_points.m order by np.m limit 1)', db=db)
        runQuery('update original_points set next_m = (select m from original_points as np where np.m>original_points.m order by np.m limit 1)', db=db)
        runQuery('delete from corrected_points', db=db)
        runQuery('insert into corrected_points(m,id,next_id,next_m,pt) select m,id,next_id,next_m,pt from original_points', db=db)
        db.commit()


    @staticmethod
    #-> [(x,y,pixel,line)]
    def gcps(frame, n = 3):
        mo = np.empty((n*2,2))
        mo.fill(np.nan)
        mo[:,0][0:n] = np.linspace(frame*HEIGHT-HEIGHT,frame*HEIGHT,n)
        mo[:,1][0:n] = -WIDTH/2
        mo[:,0][n:] = np.linspace(frame*HEIGHT-HEIGHT,frame*HEIGHT,n)
        mo[:,1][n:] = WIDTH/2
       # print(mo)
        xy = gpsModel.point(mo,corrected=True)
        lines = np.linspace(LINES,0,n).astype(int)
        r =  [(row[0],row[1],0,lines[i]) for i,row in enumerate(xy[0:n])] + [(row[0],row[1],PIXELS,lines[i]) for i,row in enumerate(xy[n:])]
      #  q = runQuery('select new_x,new_y,pixel,line from corrections where frame_id=:frame',values={':frame':frame})
     #   while q.next():
     #       r.append((q.value(0),q.value(1),q.value(2),q.value(3)))
        return r


    @staticmethod
    def setCorrections(corrections=None): 
        
    #find original x,y for corrections
    #find xy shifts to new xy and interpolate each point.
        db = defaultDb()
        db.transaction()
        q = runQuery('select frame_id,line,pixel,new_x,new_y,pk from corrections order by :height*(frame_id-line/:lines)',values={':height':HEIGHT,':lines':LINES},db=db)
        mo = []
        newXY = []
        pks = []
        while q.next():
            mo.append((lineToM(frame=q.value(0),line=q.value(1)),pixelToOffset(q.value(2))))
            newXY.append((q.value(3),q.value(4)))
            pks.append(q.value(5))
  
        mo = np.array(mo)
        m = mo[:,0]
     #   print('mo',mo)
        newXY = np.array(newXY)
      #  print('newXY',newXY)
        og = gpsModel.point(mo,corrected=False)
     #   print('og',og)
        runQuery('delete from corrected_points',db=db)
        
        
        if len(mo)>1:
            q = prepareQuery('''insert into corrected_points(id,m,next_id,next_m,pt) select id,m,next_id,next_m,
            MakePoint(:m00 * st_x(pt) + :m01 * st_y(pt) + :m02,
            :m10*st_x(pt) + :m11 * st_y(pt) + :m12,
            27700)
            from original_points 
            where m>=:s and m<:e''',db=db)
            
            def setTransform(t,startM,endM):
                q.bindValue(':s',float(startM))
                q.bindValue(':e',float(endM))
                q.bindValue(':m00',float(t[0,0]))
                q.bindValue(':m01',float(t[0,1]))
                q.bindValue(':m02',float(t[0,2]))
                q.bindValue(':m10',float(t[1,0]))
                q.bindValue(':m11',float(t[1,1]))
                q.bindValue(':m12',float(t[1,2]))
                if not q.exec():
                    raise queryError(q)
                print(t,startM,endM)
                    
            for i,mVal in enumerate(m[1:],start=1):#m values skiping 1st
                s = m[i-1]
                e = m[i]
                #trs(p1,c1,p2,c2)
                t = trs(og[i-1],newXY[i-1],og[i],newXY[i])
                setTransform(t,s,e)
                
                #translation only before 1st correction
            runQuery('insert into corrected_points(id,m,next_id,next_m,pt) select id,m,next_id,next_m,ShiftCoordinates(pt,:xs,:ys) from original_points where m<:e ',
                             values={':xs':float(newXY[0,0]-og[0,0]),':ys':float(newXY[0,1]-og[0,1]),':e':float(mo[0,0])},db=db)
       
            runQuery('insert into corrected_points(id,m,next_id,next_m,pt) select id,m,next_id,next_m,ShiftCoordinates(pt,:xs,:ys) from original_points where m>=:s ',
                             values={':xs':float(newXY[-1,0]-og[-1,0]),':ys':float(newXY[-1,1]-og[-1,1]),':s':float(mo[-1,0])},db=db)
            
            
        elif len(mo) == 0:
            print('no corrections')
            runQuery('insert into corrected_points(id,m,next_id,next_m,pt) select id,m,next_id,next_m,pt from original_points',db=db)

        elif len(mo) == 1:
            print('1 correction')
            shift = newXY[0] - og[0]
            xs = float(shift[0])
            ys = float(shift[1])
            print(xs)
            runQuery('insert into corrected_points(id,m,next_id,next_m,pt) select id,m,next_id,next_m,ShiftCoordinates(pt,:xs,:ys) from original_points ',values={':xs':xs,':ys':ys},db=db)
   
        db.commit()
        

    #-> numpy float array.
    @staticmethod
    def mo(points,minM = 0 ,maxM = maxM,corrected = False,maxDist = None):
        if corrected:
            t = 'corrected_lines'
        else:
            t = 'original_lines'
        qs = '''select start_m+(end_m-start_m)*line_locate_point(line,makePoint(:x,:y,27700)) as m
        ,st_x(startPoint(line)) as startX
        ,st_y(startPoint(line)) as startY
        ,start_m
        ,st_x(endPoint(line)) as endX
        ,st_y(endPoint(line)) as endY
        ,end_m
        from {t} where end_m >= :s and start_m < :e
        order by distance(line,makePoint(:x,:y,27700))
        limit 1'''.format(t=t)
        q = QSqlQuery(qs,defaultDb())
        if not q.prepare(qs):
            raise queryPrepareError(q)
        r = np.empty((len(points),2),dtype = np.float)
        r.fill(np.nan)
        for i,p in enumerate(points):
            q.bindValue(':s',minM)
            q.bindValue(':e',maxM)
            q.bindValue(':x',p.x())
            q.bindValue(':y',p.y())
            if not q.exec():
                raise queryError(q)
            while q.next():
                v = locatePoint(startX = q.value(1),
                            startY = q.value(2),
                            startM = q.value(3),
                            endX = q.value(4),
                            endY = q.value(5),
                            endM = q.value(6),
                            x = p.x(),
                            y = p.y())
                r[i,0] = v[0]
                r[i,1] = v[1]
        return r


    #perpendicular unit vector
    @staticmethod
    def perp(mVals,corrected = False):
        f = gpsModel.centPoint(mVals+W,corrected) - gpsModel.centPoint(mVals-W,corrected)
        r = np.empty((len(mVals),2),dtype=np.float) * np.nan
        r[:,0] = -1 * f[:,1]
        r[:,1] =  f[:,0]
        return normalizeRows(r)
    
    
    @staticmethod
    #iterable of m values -> array[x,y]
    def centPoint(mVals,corrected=False):
        if corrected:
            t = 'corrected_lines'
        else:
            t = 'original_lines'        
        qs = '''select st_x(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
        ,st_y(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
         from {t}
         where end_m >= :m - 0.001 and start_m < :m + 0.001
         '''.format(t=t)
      #  print(qs,mVals)
        q = QSqlQuery(defaultDb())
        if not q.prepare(qs):
            raise queryPrepareError(q)
        r = np.empty((len(mVals),2),dtype='float')
        r.fill(np.nan)
        for i,m in enumerate(mVals):
         #   print(qs.replace(':m',str(m)))
            q.bindValue(':m',float(m))#bindValue does not work with numpy types
        #    print(q.boundValues())
            if q.exec():
                while q.next():
                    r[i,0] = q.value(0)
                    r[i,1] = q.value(1)
            else:
                raise queryError(q)
         #   print(q.executedQuery())
        return r
            
    
    @staticmethod
    # -> array
    def point(mo,corrected=False):
        m = mo[:,0]
#        print('cent',gpsModel.centPoint(mVals = m,corrected = corrected))
        return gpsModel.centPoint(m,corrected) + gpsModel.perp(mVals= m,corrected = corrected) * mo[:,1][:,np.newaxis]
        
        


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
    def rowCount():
        q = runQuery('select count(m) from original_points')
        while q.next():
            return q.value(0)
    
    
    def pointToPixelLine(self,point,frame):
        minM = frameToM(frame)
        maxM = minM+HEIGHT
        v = self.mo(points = [point],minM = minM,maxM = maxM,corrected = True)
        return (offsetToPixel(v[0,1]),mToLine(v[0,0],frame=frame))


    #->QgsPointXY
    def FPLToPoint(self,frame,pixel,line):
        m = lineToM(frame=frame,line=line)
        offset = pixelToOffset(pixel)
        p = self.point(np.array([[m,offset]]),corrected=True)
        if len(p)>0:
            return QgsPointXY(p[0,0],p[0,1])
        return QgsPointXY()
       



    #start of uncorrected frame
    @staticmethod
    def pointToFrame(point,maxDist = 10):
        qs = '''
        select start_m+(end_m-start_m)*line_locate_point(line,makePoint(:x,:y,27700)) as m
        from original_lines where distance(line,makePoint(:x,:y,27700)) <= :d
        order by distance(line,makePoint(:x,:y,27700))
        limit 1'''
        q = runQuery(qs,values={':x':point.x(),':y':point.y(),':d':maxDist})
        while q.next():
            m = q.value(0)
            return mToFrame(m)
        return -1



    #qgsPointXY for start of uncorrected frame
    @staticmethod    
    def frameToPoint(frame):
        qs = '''select st_x(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
        ,st_y(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
         from original_lines
         where end_m >= :m - 0.0001 and start_m < :m + 0.0001 limit 1'''
        q = runQuery(qs,values={':m':frameToM(frame)})
        while q.next():
            return QgsPointXY(q.value(0),q.value(1))
        return QgsPointXY()



    @staticmethod
    def hasGps():
        return gpsModel.rowCount() > 0
