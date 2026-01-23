# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:12:37 2023

@author: Drew.Bennett

mypy runs.py --follow-imports=silent"""

from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtCore import Qt
import typing
from image_loader.db_functions import runQuery,defaultDb,prepareQuery,queryError
from image_loader import georeference_process , settings ,  dims
from image_loader.backend import runs_functions
#from image_loader.process_runner import runProcesses
from image_loader.gps import gpsSystem

from image_loader.vrt import vrtDataFromRuns,makeRunsVrt
from image_loader import layer_functions
from image_loader.process_runner import runProcesses

from qgis.core import QgsPointXY
from image_loader.gps import MO


def allRunPks() -> list[int]:
    q = runQuery('select pk from runs')
    pks = []
    while q.next():
        pks.append(q.value(0))        
    return pks
        



def imagePksFromRun(runPks:list[int]) -> list[int]:
    qs = '''
select distinct(images.pk) from runs
inner join images on frame_id >= start_frame and frame_id <= end_frame
and runs.pk in ({pks}) and runs.mfv_number = images.mfv_number order by frame_id
    '''.format(pks = ','.join([str(pk) for pk in runPks]))
 #   print(qs)

    q = runQuery(qs)
    imageKeys = []
    while q.next():
        imageKeys.append(q.value(0))        
    return imageKeys
    
    
    
    
    
    
    

    
class runsModel(QSqlQueryModel):
    
    __slots__  = ('mfv','gpsModel','gps')
    
    def __init__(self,db=None,parent=None):
        super().__init__(parent)
        self.mfv = ''
        self.select()
        self.gpsModel = None
        self.gps:gpsSystem = None
        
    def setMfv(self,mfv:str):
        self.mfv = mfv
        
      
    def database(self):
        return defaultDb()
    
    
    def fieldIndex(self,field):
        return self.record().indexOf(field)
    
    
    def fieldName(self,field):
       return self.record().fieldName(field)
    
    
    def flags(self,index):
        if index.column() == self.fieldIndex('number'):
            return Qt.ItemIsSelectable|Qt.ItemIsEnabled
        return Qt.ItemIsEnabled|Qt.ItemIsSelectable|Qt.ItemIsEditable
        
    
    def clear(self):
        runQuery('delete from runs')
        self.select()
        
    
    #[{start_frame,end_frame}]
    def addRuns(self,runs:typing.Iterable[dict]):
        runs_functions.insertRuns(runs)
        self.select()
        
        
    def addRun(self,mfv:str,startFrame:int,endFrame:int):
        db = defaultDb()
        db.transaction()
        q = prepareQuery('insert OR IGNORE into runs(mfv_number,start_frame,end_frame) values (:mfv,:s,:e)')
        q.bindValue(':mfv',mfv)
        q.bindValue(':s',startFrame)
        q.bindValue(':e',endFrame)
        q.exec()
        db.commit()
        self.select()
        
        
        
    def select(self):
        #q = 'select ROW_NUMBER() over (order by start_frame,end_frame) as number,pk ,start_frame,end_frame,chainage_correction,left_offset from runs order by start_frame,end_frame'
        q = "select start_frame||' to '||end_frame as frames,pk,start_frame,end_frame,chainage_shift,offset,correction_start_m,correction_end_m,correction_start_offset,correction_end_offset from runs_view where mfv_number = '{mfv}' order by start_frame,end_frame".format(mfv = self.mfv)   
        self.setQuery(q,self.database())
        
     
    def data(self,index,role=Qt.DisplayRole):
        #start_frame and end_frame should be int but default gives str. sqlite weirdness?
        if role == Qt.EditRole and index.column() in (self.fieldIndex('start_frame'),self.fieldIndex('end_frame')):
            return int(super().data(index,role))
        return super().data(index,role)   
        
    
    #correction_start_m and correction_start_offset = 0 if editing table. otherwise where user clicked.
    def setData(self,index,value,role=Qt.EditRole):
        if role == Qt.EditRole and value != index.data():
        #    print('setData',index.row(),index.column(),value)
             
            pk = self.index(index.row(),self.fieldIndex('pk')).data()
            q = 'update runs set {col} = :val where pk = :pk'.format(col = self.fieldName(index.column()))

            if index.column() == self.fieldIndex('chainage_shift'):
                q = 'update runs set correction_start_m = 0.0, correction_end_m = :val where pk = :pk'
           
            if index.column() == self.fieldIndex('offset'):
                q = 'update runs set correction_start_offset = 0.0, correction_end_offset = :val where pk = :pk'
                
          #  print(q,'val',value,'pk',pk)
            runQuery(query = q,values = {':pk':pk,':val':value})
            self.select()
            return True
        return super().setData(index,value,role)
    
    
    def paste(self,text):
        runs_functions.loadText(text,mfv = self.mfv)
        self.select()
    
    
    def setCorrection(self , pk:int , startM:float , endM:float , startOffset:float , endOffset:float):
        qs = '''update runs set correction_start_m = :s - correction_end_m +correction_start_m , 
        correction_start_offset = :so - correction_end_offset + correction_start_offset, 
        correction_end_m = :e , correction_end_offset = :eo where pk = :pk'''
        runQuery(query = qs,values = {':pk':pk,':s':startM,':e':endM,':so':startOffset,':eo':endOffset})
        self.select()


    #pks:[int]
    def dropRuns(self,pks):
   #     print('pks',pks)
        pks = [str(pk) for pk in pks]
        q = 'delete from runs where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        runQuery(q)
        self.select()

        
    def findFrame(self , row:int , x:float , y:float) -> int:
        #self.mfv
        #only need nearest to find nearest multiple of HEIGHT to point.
        
        return 0


    #used by chainagesDialog.
    #QgsGeometry in model srid
 #   def centerLine(self , startFrame : int , endFrame : int)  -> QgsGeometry:
  #      xy = self.splineString.centerLinePoint(np.arange(startM , endM , dims.HEIGHT))#[(x1,y1),(x2,y2)...]
  #      return QgsGeometry.fromPolylineXY([QgsPointXY(row[0],row[1]) for row in xy])
    






    def processRuns(self, gps:gpsSystem , runPks:list[int]):
        print('processRuns',runPks,'mfv:',self.mfv)
        #unload layers with  images and vrt files containing them.
      #  vrtSources = [v.vrtFile for v in vrtDataFromRuns(runPks = runPks)]
     #   print(vrtSources)
        #georeference
      #  self.georeferenceRuns()
       # self.makeRunsVrt()
     #   self.loadRunsVrt()
     
      #  imagePks = imagePksFromRun(runPks)
      #  print(imagePks)
     
        
         #recalculate gcp table
        db = self.database()
        db.transaction()
        
        frames = []
        pkCol = self.fieldIndex('pk')
        startFrameCol = self.fieldIndex('start_frame')
        endFrameCol = self.fieldIndex('end_frame')
        chainageShiftCol = self.fieldIndex('chainage_shift')
        offsetCol = self.fieldIndex('offset')

        deleteQuery = prepareQuery("delete from gcp where frame = :frame and mfv_number = :mfv",db = db)
        insertQuery = prepareQuery('insert into gcp(mfv_number,frame,pixel,line,x,y) values (:mfv,:frame,:pixel,:line,:x,:y)',db = db)


        for row in range(self.rowCount()):
            if self.index(row,pkCol).data() in runPks:
                s = self.index(row,startFrameCol).data()
                e = self.index(row,endFrameCol).data()
                shift = self.index(row,chainageShiftCol).data()
                offset = self.index(row,offsetCol).data()

                for frame in range(s,e+1):
                    
                    deleteQuery.bindValue(':frame',frame)
                    deleteQuery.bindValue(':mfv',self.mfv)
                    if not deleteQuery.exec():
                        raise queryError(deleteQuery)
                          
                    frames.append(frame)
                    for p in gps.currentCurve().gcps(frame = frame,chainageShift=shift,offset=offset):
                        insertQuery.bindValue(':x',p.x)
                        insertQuery.bindValue(':y',p.y)
                        insertQuery.bindValue(':pixel',p.pixel)
                        insertQuery.bindValue(':line',p.line)
                        insertQuery.bindValue(':frame',frame)
                        insertQuery.bindValue(':mfv',self.mfv)
                        if not insertQuery.exec():
                            raise queryError(insertQuery)
        
        db.commit()
        
        vrtD = vrtDataFromRuns(runPks)
        
        
        #unload vrt layers
        for v in vrtD:
            v.removeSources()
            
        
        #remove image layers.
        
        imagePks = imagePksFromRun(runPks)
     
        georeferenceProcesses , sources , errors = georeference_process.georeferenceProcesses(imagePks = imagePks)
        
      #  for e in errors:
      #      print(e)
        
        if georeferenceProcesses:
            layer_functions.removeSources(sources)
            
        runProcesses(parent = self.parent() , processes = georeferenceProcesses , labelText = 'Georeferencing runs')
        
        #shows dialog
        makeRunsVrt(vrtD)
        
        
        for v in vrtD:
            v.load()

    # array of [[m,o]] ordered by distance
    #run should only pass near point once...
   # def locate(self , row : int, point:QgsPointXY) -> np.array:
   #     outsideRunDistance = settings.outsideRunDistance()
    #    minM = dims.frameToM(int(self.index(row , self.fieldIndex('start_frame')).data())) - outsideRunDistance
    #    maxM = dims.frameToM(int(self.index(row , self.fieldIndex('end_frame')).data())) + outsideRunDistance
    #    return self.gpsModel.locate(x = point.x() , y = point.y() , minM = minM , maxM = maxM )#nearest within range.



    def locate(self,row:int , point:QgsPointXY) -> list[MO]:
        startCol = self.fieldIndex('start_frame')
        endCol = self.fieldIndex('end_frame')
        startFrame = self.index(row,startCol).data()
        endFrame = self.index(row,endCol).data()
        if startFrame is None:
            raise ValueError('no start frame for run')
        if endFrame is None:
            raise ValueError('no end frame for run')
        minM = dims.frameToM(startFrame) - settings.outsideRunDistance()
        maxM = dims.frameToM(endFrame+1) + settings.outsideRunDistance()
        return [self.gps.currentCurve().findMO(point,minM = minM,maxM = maxM)]
        
        
        

    def georeferenceRuns(self, runPks:list[int]):
        pass
