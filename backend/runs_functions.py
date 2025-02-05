# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 10:06:38 2025

@author: Drew.Bennett
"""
from qgis.utils import iface
from PyQt5.QtSql import QSqlQueryModel
import numpy as np
import csv
import io
from qgis.core import QgsGeometry
import typing
from image_loader.db_functions import runQuery,defaultDb
from image_loader.type_conversions import asFloat
from image_loader import settings , db_functions , dims
from qgis.core import QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsProject
import math



#fields = ['RunID','FromFrame','ToFrame','Chainage','Offset','StartX','StartY','EndX','EndY']
            
#generator {}
def parseCsv(f:typing.TextIO , quiet : bool = False):
    
    lines = [line.strip().lower() for line in f.readlines()]
    
    #print('lines',lines)
    if lines[0] == 'start_frame\tend_frame\tchainage_shift\toffset':
        fieldNames = ['fromframe','toframe','chainage','offset']
        reader = csv.DictReader(lines[1:],fieldnames=fieldNames,dialect='excel',delimiter = '\t')
    else:
        reader = csv.DictReader(lines,dialect='excel',delimiter = ',')
    
    for row in reader:
        #print(row)
        try:
            yield {'start_frame':int(row.get('fromframe')),
                   'end_frame':int(row.get('toframe')),
                   'chainage_shift':asFloat(row.get('chainage'),0.0),
                   'offset':asFloat(row.get('offset'),0.0)}
        except Exception as e:
            if not quiet:
                print(row)
                print(e)
      
    
def saveRunsCsv(file:str):
    with open(file,'w',newline='') as f:
        writer = csv.writer(f,dialect='excel',delimiter = ',')
        writer.writerow(('RunID','FromFrame','ToFrame','Chainage','Offset','StartX','StartY','EndX','EndY'))
        q = runQuery('select start_frame,end_frame,chainage_shift,offset from runs_view order by number')
        row = 1
        while q.next():
            writer.writerow((row,q.value(0),q.value(1),q.value(2),q.value(3)))
            row += 1




def imagePksFromRun(runPks):
    qs = '''
select distinct(images.pk) from runs
inner join images on frame_id >= start_frame and frame_id <= end_frame
and runs.pk in ({pks})
    '''.format(pks = ','.join([str(pk) for pk in runPks]))
 #   print(qs)

    q = runQuery(qs)
    imageKeys = []
    while q.next():
        imageKeys.append(q.value(0))        
    return imageKeys
    

def insertRuns(runs):
    db = db_functions.defaultDb()
    db.transaction()
    q = db_functions.prepareQuery('insert OR IGNORE into runs(start_frame,end_frame) values (:s,:e)')
    for r in runs:
        q.bindValue(':s',r['start_frame'])
        q.bindValue(':e',r['end_frame'])
        q.exec()
    db.commit()
    
    
    
def addRows(data,clear = False):
    db = db_functions.defaultDb()
    db.transaction()
    if clear:
        runQuery(query = 'delete from runs', db=db)
    for r in data:
        sm = dims.frameToM(r['end_frame'])
        em = sm + r['chainage_shift']
        runQuery(query = 'insert OR IGNORE into runs(start_frame,end_frame,correction_start_m,correction_end_m,correction_end_offset) values (:s,:e,:sm,:em,:eo)',
                    db=db,values = {':s':r['start_frame'],
                                     ':e':r['end_frame'],
                                     ':sm':sm,
                                     ':em':em,
                                     ':eo':r['offset']})
    db.commit()
    
    
#rename to loadStr
#load text from excel via clipboard etc
def loadText(text:str):
    f = io.StringIO('start_frame\tend_frame\tchainage_shift\toffset\n'+text)
    addRows(parseCsv(f))


def loadCsv(file:str):
    with open(file,'r') as f:
        addRows(parseCsv(f),clear=True)    
    
    
    
#iterable of QgsFeature.
#[{start_frame,end_frame}]
#returns frames within area of polygon and direction within maxAngle of bearing or opposite.
#maxAngle in degrees
def runsFromAreas(features , crs : QgsCoordinateReferenceSystem , bearingField , maxAngle = 25) -> list:
    db = db_functions.defaultDb()
    db.transaction()
    
    #upload areas layer
    q = db_functions.runQuery('delete from areas', db = db)
    q = db_functions.prepareQuery('insert into areas(area , bearing) values (ST_PolyFromText(:a,4326),:b)', db = db)    
    targetCrs = QgsCoordinateReferenceSystem('ESPG:4326')
    transform = QgsCoordinateTransform(crs,targetCrs,QgsProject.instance())
    for f in features:
        g = f.geometry()
        g.transform(transform)
        q.bindValue(':a',g.asWkt())
        if bearingField:
            q.bindValue(':b',f[bearingField])
        else:
            q.bindValue(':b',None)
        q.exec()
    db.commit()
    
    
    qs = '''select m
,last != last_id or last_id is null or last is null as rising
,next != next_id or next_id is null or next is null as falling
from 
	(
	select area_pk,dot>0 as f,m,id,next_id,last_id
	,lead(id) over (order by area_pk,dot>0,m) as next
	,lag(id) over (order by area_pk,dot>0,m) as last
	from areas_join_1 where abs(dot) > :a or dot is null
	)
where last != last_id or last_id is null or last is null or next != next_id or next_id is null or next is null
order by m
'''
 
    q = db_functions.runQuery(qs,db=db,values = {':a':math.cos(math.radians(maxAngle))})#:a = cos(max_angle)

    ranges = []#[[startM,endM]]
    while q.next():
        frame = dims.mToFrame(q.value(0))
        if q.value(1) == True:
            ranges.append({'start_frame':frame,'end_frame':frame})
        if q.value(1) == False:
            ranges[-1]['end_frame'] = frame
    return ranges








