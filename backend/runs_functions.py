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
from image_loader import settings , db_functions , dims , vrt , georeference
from qgis.core import QgsCoordinateReferenceSystem,QgsCoordinateTransform,QgsProject
import math
import os





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
      
    

def allRunPks():
    q = runQuery('select pk from runs')
    pks = []
    while q.next():
        pks.append(q.value(0))        
    return pks
    




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
    


def clearRuns():
    runQuery(query = 'delete from runs')


#iterable of dict
#returns list of run pk
def addRuns(runs):
    db = db_functions.defaultDb()
    db.transaction()
    q = db_functions.prepareQuery('insert OR IGNORE into runs(start_frame,end_frame) values (:s,:e) returning pk')
    pks = []
    for r in runs:
        q.bindValue(':s',r['start_frame'])
        q.bindValue(':e',r['end_frame'])
        q.exec()
        q.next()
        pks.append(q.value(0))
    db.commit()
    return pks
    
    
    
#rename to loadStr
#load text from excel via clipboard etc
def loadText(text:str):
    f = io.StringIO('start_frame\tend_frame\tchainage_shift\toffset\n'+text)
    addRuns(parseCsv(f))


def loadCsv(file:str):
    with open(file,'r') as f:
        clearRuns()
        addRuns(parseCsv(f))    
    
    
    
#iterable of QgsFeature.
#[{start_frame,end_frame}]
#returns frames within area of polygon and direction within maxAngle of bearing or opposite.
#maxAngle in degrees
def runsFromAreas(features , crs : QgsCoordinateReferenceSystem , bearingField , maxAngle = 25) -> list:
    featureSrid = crs.postgisSrid()
    db = db_functions.defaultDb()
    db.transaction()
    
    #upload areas layer
    q = db_functions.runQuery('delete from areas', db = db)
    q = db_functions.prepareQuery('insert into areas(area , bearing) values (ST_Transform(ST_PolyFromText(:a,:featureSrid),:srid),:b)', db = db)    
    targetCrs = settings.destCrs()
    
    for f in features:       
        q.bindValue(':a',f.geometry().asWkt())
        q.bindValue(':srid',targetCrs)
        q.bindValue(':featureSrid',featureSrid)


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
    
    return [r for r in ranges if r['end_frame'] - r['start_frame'] > 5] # minimum of 5 frames in run. make this into setting?



#data for making vrt from selected runs.
#->[vrt.vrtData]
def vrtDataFromRuns(runPks:list):
    qs = '''select image_type,start_frame,end_frame,group_concat(original_file,'[,]') from runs inner join images on frame_id >= start_frame and frame_id <= end_frame 
    and runs.pk in ({runPks})
    group by image_type,start_frame,end_frame
'''.format(runPks =  ','.join([str(pk) for pk in runPks]))

    query = db_functions.runQuery(qs)
    d = [] 
    while query.next():        
        originalFiles = query.value(3).split('[,]')
        # existing warped files
        warpedFiles = [os.path.normpath(georeference.warpedFileName(f)) for f in originalFiles if os.path.isfile(georeference.warpedFileName(f))]
        if warpedFiles:
            d.append(vrt.vrtData(imageType = query.value(0) ,
                             startFrame = query.value(1) ,
                             endFrame = query.value(2) ,
                             warpedFiles = warpedFiles))
    return d


def runFromFrame(frame:int):
    q = runQuery('select pk from runs where start_frame <= :f and end_frame >= :f limit 1',values = {':f':frame})
    q.next()
    return q.value(0)


def mRange(runPk : int):
    q = runQuery('select start_frame,end_frame from runs where pk = :pk',values = {':pk':runPk})
    while q.next():
        return (dims.frameToM(q.value(0)) , dims.frameToM(q.value(1)))
    return None
    


def frames(runPk:int) -> list:
    runsQuery = runQuery('select start_frame,end_frame from runs where pk = :pk' , values = {':pk':runPk})
    while runsQuery.next():
        return [frame for frame in range(runsQuery.value(0) , runsQuery.value(1)+1)]
    return []
        



