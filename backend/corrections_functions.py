# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 10:06:38 2025

@author: Drew.Bennett
"""
import numpy as np
from qgis.core import QgsGeometry
from image_loader import settings , db_functions , dims
from image_loader.backend import gps_functions , runs_functions
from qgis.core import QgsPointXY
from image_loader import splinestring




def insertCorrection(frame:int , line:int , pixel:int , m:float , offset:float , run:int):
    db_functions.runQuery('insert into corrections(frame,line,pixel,new_chainage,new_offset,run) values (:frame,:line,:pixel,:m,:offset,:run)',
                          values = {':frame':frame , ':line':line , ':pixel':pixel , ':m':m,':offset':offset,':run':run})



def dropCorrections(pks:list[int]):
    q = db_functions.prepareQuery('delete from corrections where pk = :pk')
    for pk in pks:
        q.bindValue(':pk',pk)
        if not q.exec():
            raise db_functions.queryError(q)



def loadCsv(filePath : str):
    pass



def saveCsv(filePath : str):
    pass




#wrong
#geometry for corrections dialog
def getCorrectionGeom(frame:int , pixel : int , line:int , chainage:float , offset:float) -> QgsGeometry:
    startM = dims.lineToM(frame = frame, line = line)
    startOffset = dims.pixelToOffset(pixel)    
    runPk = runs_functions.runFromFrame(frame)
    s = _getCorrectedSpline(runPk = runPk)
    if hasattr(s,'point'):
        sp = s.point(m = startM , offset = startOffset)
       #gps_functions.centerLine(startM , startOffset)
        points = [QgsPointXY(sp[0],sp[1])] + [gps_functions.point(chainage,offset)]
        return QgsGeometry.fromPolylineXY(points)
    return QgsGeometry()



#array [(m1,x1,y1)...]
#splineString from projected points stored in database. In whatever srid last set.
def _getCorrectedSpline(runPk:int) -> splinestring.splineString:
    q = db_functions.runQuery('select m,x,y from corrected_points where run = :run and x is not null and y is not null order by m',
                                values = {':run':runPk},
                                forwardOnly = True)
    mxy = []
    while q.next():
        mxy.append( [ float(q.value(0)) , float(q.value(1)) , float(q.value(2)) ] )
        
        
    mxy = np.array(mxy,dtype = float)
    mxy.dtype = splinestring.mxyType
    
    if len(mxy) > splinestring.K:
        return splinestring.splineString(values = mxy)
        
    
    
    
#-> '-gcp <pixel> <line> <easting> <northing>'
#might as well serialize to string here. list is valid JSON and avoids passing "" to CLI
N = 2 # GCP points per side of frame
def calcGcps(frame : int , geom : splinestring.splineString) -> str:
     startM = dims.frameToM(frame)
     endM = startM + dims.HEIGHT
     mo = np.zeros((N*2,2)) * np.nan
     mo[:,0][0:N] = np.linspace(startM,endM,N)
     mo[:,0][N:] = np.linspace(startM,endM,N)
     mo[:,1][0:N] = dims.WIDTH/2
     mo[:,1][N:] = - dims.WIDTH/2
     xy = geom.points(mo)
     r = np.zeros((N*2,4)) * np.nan
     r[:,0:2] = xy
     r[:,2][0:N] = 0
     r[:,2][N:] = dims.PIXELS
     r[:,3][0:N] = np.linspace(dims.LINES,0,N)
     r[:,3][N:] = np.linspace(dims.LINES,0,N)
     #v = [(row[0],row[1],int(row[2]),int(row[3])) for row in r]
     #-gcp <pixel> <line> <easting> <northing> [<elevation>]
     return ' '.join(['-gcp {pixel} {line} {easting} {northing}'.format(pixel = int(a[2] ), line = int(a[3]) , easting = a[0] , northing = a[1]) for a in r])
     



#uses corrected_points 
def XYToFramePixelLine(x:float , y:float , runPk:int):
    s = _getCorrectedSpline(runPk)
    
    #use original_points where no corrections yet
    if s is None:
        m,offset = gps_functions.locate(x = x , y = y , runPk = runPk)
        
    if s is not None:        
        m,offset = s.locate(x = x , y = y)
        #print('m:',m,'offset:',offset)
        
    frame = dims.mToFrame(m)
    line = dims.mToLine(m = m , frame = frame)
    pixel = dims.offsetToPixel(offset)
    return (frame , pixel , line)

    return (-1,-1,-1)



#update table. only need frames within runs in corrected_points.
def correctRun(runPk:int , db = None):
    if db is None:
        db = db_functions.defaultDb()
        
    db.transaction()
    
    

    db_functions.runQuery('delete from corrected_points where run = :run' , 
                          values = {':run':runPk} ,
                          db = db)
    
    
    mVals = [f * dims.HEIGHT for f in runs_functions.frames(runPk)]
    points = [gps_functions.MO(m,0) for m in mVals]
    insertQuery = db_functions.prepareQuery('insert into corrected_points(m,x,y,run) values (:m,:x,:y,:run)' , db = db)

    cp = correctMO(values = points , runPk = runPk)
    correctedPoints:list[QgsPointXY] = gps_functions.MOToXY(cp)

    for i,p in enumerate(correctedPoints):
        insertQuery.bindValue(':m',mVals[i])
        insertQuery.bindValue(':x',p.x())
        insertQuery.bindValue(':y',p.y())
        insertQuery.bindValue(':run',runPk)
        if not insertQuery.exec():
            raise db_functions.queryError(insertQuery)

    #print(correctedPoints)
    db.commit()


#############freezes?
def correctMO(values:list[gps_functions.MO] , runPk:int) -> list[gps_functions.MO]:
    print('values',values)
    q = db_functions.runQuery('select frame,line,pixel,new_chainage,new_offset from corrections where run = :run order by frame , line desc', values = {':run':runPk})   

    mValues = []
    mCorrections = []
    offsetCorrections = []
    
    while q.next():
        mv = dims.lineToM(frame = q.value(0), line = q.value(1))
        mValues.append(mv)
        mCorrections.append(q.value(3) - mv)
        offsetCorrections.append(q.value(4) - dims.pixelToOffset(q.value(2)))


    #values unchanged if no corrections for run
    if len(mValues) == 0:
        return values
        
    #single shift if 1 correction for run
   # if len(mValues) == 1:        
     #   return [gps_functions.MO(p.m + correctedM[0] - mValues[0] , p.offset +   offsetCorrections[0]) for p in values]


    #np.interp returns left or right for values outside xp
    if len(mValues) > 0:
        m = [p.m for p in values]
        
        correctedChainages = [p.m for p in values] + np.interp(x = m , 
                  xp = mValues , 
                  fp = mCorrections)
    
        correctedOffsets = [p.offset for p in values] + np.interp(x = m , 
                  xp = mValues , 
                  fp = offsetCorrections)
            
        r = []
        for i,ch in enumerate(correctedChainages):
            r.append(gps_functions.MO(ch,correctedOffsets[i]))
            
        print('r:\n',r)
        return r




#move this?
#currently for debugging only
from qgis.core import QgsGeometry,QgsPointXY, QgsFeature,edit,QgsVectorLayer,QgsProject
from image_loader import group_functions

def downloadCorrectedPoints() -> None:
    uri = "Point?crs=epsg:{p}&field=m:int&index=yes".format(p = settings.destSrid())    
    layer = QgsVectorLayer(uri,'corrected_centerline',"memory")
    print(layer)
    fields = layer.fields()
               
    def features():
        q = db_functions.runQuery('select m , x, y from corrected_points')
        while q.next():
            f = QgsFeature(fields)
            f['m'] = q.value(0)
            geom = QgsGeometry.fromPointXY(QgsPointXY(q.value(1),q.value(2)))
            f.setGeometry(geom)
            if f.isValid():
                yield f
                
    with edit(layer):
         layer.addFeatures(features())
  
    group = group_functions.getGroup(['image_loader'])#QgsLayerTreeGroup
    group.addLayer(layer)

    node = group.findLayer(layer)
    node.setItemVisibilityChecked(True)
    node.setExpanded(False)        
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend








def profileCorrectRun():
    runPk = 1
    correctRun(runPk)



def testCorrect():
    points  = [gps_functions.MO(0,0),gps_functions.MO(10,0)]
    r = correctMO(values = points , runPk = 1)
    print(r)
    correctRun(runPk = 1)
    _getCorrectedSpline(runPk = 1)


if __name__ == '__console__':
    testCorrect()
    #downloadCorrectedPoints()
    

