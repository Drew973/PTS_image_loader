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
from image_loader.dims import HEIGHT, offsetToPixel, mToLine,lineToM,pixelToOffset,WIDTH,LINES,PIXELS,frameToM,mToFrame,MAX,clamp
from image_loader.transforms import trs,fromTranslation,affine


def normalizeRows(a):
    s = a*a
    rowSums = np.sqrt(s.sum(axis=1))
    return a / rowSums[:, np.newaxis]


def magnitude(v):
    return np.sqrt(v.dot(v))


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
            

class gpsModel:

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
        runQuery('delete from transforms',db=db)
        
        if len(mo)>1:
            q2 = prepareQuery( 
                '''insert into transforms(start_m,end_m,t00,t01,t02,t10,t11,t12)
                values(:s,:e,:t00,:t01,:t02,:t10,:t11,:t12)
    ''')
    
            def setTransform(a,startM,endM):         
                t = a.m
                q2.bindValue(':s',float(startM))
                q2.bindValue(':e',float(endM))
                q2.bindValue(':t00',float(t[0,0]))
                q2.bindValue(':t01',float(t[0,1]))
                q2.bindValue(':t02',float(t[0,2]))
                q2.bindValue(':t10',float(t[1,0]))
                q2.bindValue(':t11',float(t[1,1]))
                q2.bindValue(':t12',float(t[1,2]))
                if not q2.exec():
                    raise queryError(q2)
                    
            for i,mVal in enumerate(m[1:],start=1):#m values skiping 1st
                s = m[i-1]
                e = m[i]
                #trs(p1,c1,p2,c2)
                a = trs(og[i-1],newXY[i-1],og[i],newXY[i])
                setTransform(a,s,e)                

            shift = newXY[0] - og[0]
            setTransform(fromTranslation(shift[0],shift[1]),0,mo[0,0])
            
            shift = newXY[-1] - og[-1]
            setTransform(fromTranslation(shift[0],shift[1]),mo[-1,0],MAX)

        elif len(mo) == 0:
            #print('no corrections')
            runQuery('insert into corrected_points(id,m,next_id,next_m,pt) select id,m,next_id,next_m,pt from original_points',db=db)

        elif len(mo) == 1:
           # print('1 correction')
            shift = newXY[0] - og[0]
            xs = float(shift[0])
            ys = float(shift[1])
          #  print(xs)
            runQuery('insert into corrected_points(id,m,next_id,next_m,pt) select id,m,next_id,next_m,ShiftCoordinates(pt,:xs,:ys) from original_points ',values={':xs':xs,':ys':ys},db=db)
   
        db.commit()
        

    #-> numpy float array.
    @staticmethod
    def mo(points,minM = 0 ,maxM = maxM,corrected=False,maxDist = None):
        r = np.empty((len(points),2),dtype = np.float)
        r.fill(np.nan)
        qs = '''select start_m+(end_m-start_m)*line_locate_point(line,makePoint(:x,:y,27700)) as m
        ,st_x(ClosestPoint(line,makePoint(:x,:y,27700)))
        ,st_y(ClosestPoint(line,makePoint(:x,:y,27700)))
        from original_lines where end_m > :s and start_m < :e
        order by distance(line,makePoint(:x,:y,27700))
        limit 1'''
        q = QSqlQuery(qs,defaultDb())
        if not q.prepare(qs):
            raise queryPrepareError(q)

      #  print('minM',minM)
      #-> array[m,offset]
      #some discrepencies when nearest point is vertex.
        def locate(op):
            print('locate',op)
            r = np.array([np.nan,np.nan],dtype = np.float)
            q.bindValue(':s',minM)
            q.bindValue(':e',maxM)
            q.bindValue(':x',op.x())
            q.bindValue(':y',op.y())
            if not q.exec():
                raise queryError(q)
            while q.next():
                r[0] = q.value(0)
                print('m',q.value(0))
                nearest = QgsPointXY(q.value(1),q.value(2))
                print('dist',nearest.distance(op))
                print('nearest',nearest)
                pn = np.array([q.value(1)-op.x(),q.value(2)-op.y()],dtype = np.float)#point to nearest
                perp = gpsModel.perp(np.array([clamp(r[0],minM,maxM)]))#left perpendicular
                if len(perp)>0:
                    perp  = perp[0]
                    r[1] = - np.dot(pn,perp)
            return r
                
        if corrected:
            transforms = [t for t in gpsModel.getTransforms(minM,maxM)]
        else:
            transforms = None
            
        for i,p in enumerate(points):
            if transforms:
                print('p',p,'uncorrect:',transforms[0].reverse(p))
                v = np.array([locate(t.reverse(p)) for t in transforms],dtype = np.float)
                print('v',v)
                ind = np.argmax(np.absolute(v[:,1]))#row with minimum offset
                r[i,0] = v[ind,0]
                r[i,1] = v[ind,1]
            else:
                v = locate(p)
                r[i,0] = v[0]
                r[i,1] = v[1]
        return r


    #perpendicular unit vector
    #mVals: array
    @staticmethod
    def perp(mVals,corrected = False):
        f = gpsModel.centPoint(mVals+W) - gpsModel.centPoint(mVals-W)
        r = np.empty((len(mVals),2),dtype=np.float) * np.nan
        r[:,0] = -1 * f[:,1]
        r[:,1] =  f[:,0]
        return normalizeRows(r)
    
    @staticmethod
    def tangent(mVals):
        return normalizeRows(gpsModel.centPoint(mVals+W) - gpsModel.centPoint(mVals-W))
    
    
    
    @staticmethod
    #iterable of m values -> array[x,y]
    def centPoint(mVals):
      
        qs = '''select st_x(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
        ,st_y(ST_Line_Interpolate_Point(line,(:m-start_m)/(end_m-start_m)))
         from original_lines
         where end_m >= :m - 0.001 and start_m < :m + 0.001
         '''
        q = QSqlQuery(defaultDb())
        if not q.prepare(qs):
            raise queryPrepareError(q)
        r = np.empty((len(mVals),2),dtype=np.float)
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
   
    #list of transform arrays.
    @staticmethod        
    def getTransform(m):
        qs = '''
        select
        t00,t01 ,t02,t10,t11,t12 as y
        from transforms 
        where start_m <= :m and end_m >:m
        limit 1
        '''
        q = prepareQuery(qs)
        transforms = []
        for mVal in m:
            q.bindValue(':m',float(mVal))
            if not q.exec():
                raise queryError(q)
            while q.next():
                transforms.append(affine(a = q.value(0),
                       b = q.value(1),
                       c = q.value(2),
                       d = q.value(3),
                       e = q.value(4),
                       f = q.value(5)))
        return transforms
        
    #all transforms for m range
    @staticmethod        
    def getTransforms(startM,endM):
        qs = '''
        select
        t00,t01,t02,t10,t11,t12
        from transforms 
        where end_m >= :s and start_m <= :e
        '''
        q = runQuery(qs,values = {':s':float(startM),':e':float(endM)})
        while q.next():
            yield affine(a = q.value(0),
                   b = q.value(1),
                   c = q.value(2),
                   d = q.value(3),
                   e = q.value(4),
                   f = q.value(5))
        
        
    @staticmethod
    # -> array
    def point(mo,corrected=False):
        m = mo[:,0]
#        print('cent',gpsModel.centPoint(mVals = m,corrected = corrected))
        xy = gpsModel.centPoint(m) + gpsModel.perp(mVals= m) * mo[:,1][:,np.newaxis]
        if corrected:
            transforms = gpsModel.getTransform(m)#list
            for i,t in enumerate(transforms):
                p = t.forward(QgsPointXY(xy[i,0],xy[i,1]))
                xy[i] = [p.x(),p.y()]
        return xy


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
    
    
    #corrected point -> (int,int)
    @staticmethod
    def pointToPixelLine(point,frame):
        minM = frameToM(frame)
        maxM = minM + HEIGHT        
        v = gpsModel.mo(points = [point],minM = minM,maxM = maxM,corrected = True)
   #     print('v',v)
        print(v[0,1])
        return (offsetToPixel(v[0,1]),mToLine(v[0,0],frame=frame))


    #->QgsPointXY
    #frame,pixel,line to corrected point
    @staticmethod
    def FPLToPoint(frame,pixel,line):
        m = lineToM(frame=frame,line=line)
        offset = pixelToOffset(pixel)
        p = gpsModel.point(np.array([[m,offset]]),corrected=True)
        if len(p)>0:
            return QgsPointXY(float(p[0,0]),float(p[0,1]))
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
