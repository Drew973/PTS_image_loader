# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:12:37 2023

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlQueryModel
from PyQt5.QtCore import Qt
import numpy as np
import csv
import io
from qgis.core import QgsPointXY

from image_loader.dims import mToFrame,MAX,frameToM
from image_loader.db_functions import runQuery,defaultDb,prepareQuery,queryError
from image_loader.image_model import imageModel
from typing import Tuple

def tryFloat(v,default = 0.0):
    try:
        return float(v)
    except Exception:
        return default


def parseCsv(file):
    reader = csv.reader(file,dialect='excel',delimiter = '\t')
        
    for row in reader:
            #print(row)
        try:
            startFrame = int(row[0].strip())
            endFrame = int(row[1])
                
            try:
                chainageShift = float(row[2].strip())
            except Exception:
                chainageShift = 0.0
                    
            try:
                offset = float(row[3].strip())
            except Exception:
                offset = 0.0                    
                
            yield {'start_frame':startFrame,'end_frame':endFrame,'chainage_shift':chainageShift,'offset':offset}
                               
        except Exception as e:
            print(e)


class runsTableModel(QSqlQueryModel):
    
    def __init__(self,db=None,parent=None):
        super().__init__(parent)
        self.select()
        self.gpsModel = None
        
      
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
    def addRuns(self,runs):
        db = self.database()
        db.transaction()
        for r in runs:
            runQuery(query = 'insert OR IGNORE into runs(start_frame,end_frame) values (:s,:e)',
                     db=db,values = {':s':r['start_frame'],':e':r['end_frame']})    
        db.commit()
        self.select()
        
        
    def select(self):
        #q = 'select ROW_NUMBER() over (order by start_frame,end_frame) as number,pk ,start_frame,end_frame,chainage_correction,left_offset from runs order by start_frame,end_frame'
        q = 'select number,pk ,start_frame,end_frame,chainage_shift,offset,correction_start_m,correction_end_m,correction_start_offset,correction_end_offset from runs_view order by start_frame,end_frame'       
        self.setQuery(q,self.database())
        
     
  #  #def data(self,index,role=Qt.DisplayRole):
      #  if role in (Qt.EditRole,Qt.DisplayRole) and index.column() == self.fieldIndex('number'):
       #     d = super().data(index,role)
       #     return int(d)
     #   return super().data(index,role)        
        
    
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
    
    
    def setCorrection(self,pk,startM,endM,startOffset,endOffset):
        qs = '''update runs set correction_start_m = :s - correction_end_m +correction_start_m , 
        correction_start_offset = :so - correction_end_offset + correction_start_offset, 
        correction_end_m = :e , correction_end_offset = :eo where pk = :pk'''
        runQuery(query = qs,values = {':pk':pk,':s':startM,':e':endM,':so':startOffset,':eo':endOffset})
        self.select()

    
    def dropRuns(self,pks):
   #     print('pks',pks)
        pks = [str(pk) for pk in pks]
        q = 'delete from runs where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        runQuery(q)
        self.select()
        
        
        
    def imagePks(self,runPks):
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
        
        
    
    def georeference(self,gpsModel,pks):
    #    print('run pks',pks)
        qs = '''
select distinct(images.pk) from runs_view
inner join images on frame_id >= start_frame and frame_id <= end_frame
and runs_view.pk in ({pks})
        '''.format(pks = ','.join([str(pk) for pk in pks]))
     #   print(qs)
    
        q = runQuery(qs)
        imageKeys = []
        while q.next():
            imageKeys.append(q.value(0))
        
        imageModel.georeference(gpsModel = self.gpsModel , pks = imageKeys)
        imageModel.makeVrt(imageKeys)
        
   #     qs = '
#select number,image_type from runs_view
#inner join images on frame_id >= start_frame and frame_id <= end_frame
#and runs_view.pk in ({pks})
#group by runs_view.pk,image_type
#        '.format(pks = ','.join([str(pk) for pk in pks]))
        
        
   #     q = runQuery(qs)
  #      while q.next():
    #        imageKeys.append(q.value(0))
       
    
    def loadText(self,text):
        f = io.StringIO(text)
        self.addRows(parseCsv(f))
    
    
    def loadCsv(self,file):
        with open(file,'r', newline='') as f:
            self.addRows(parseCsv(f))
            
          
        
        
    def addRows(self,data,clear = False):
        db = self.database()
        db.transaction()
        if clear:
            runQuery(query = 'delete from runs', db=db)
        for r in data:
            sm = frameToM(r['end_frame'])
            em = sm + r['chainage_shift']
                
            runQuery(query = 'insert OR IGNORE into runs(start_frame,end_frame,correction_start_m,correction_end_m,correction_end_offset) values (:s,:e,:sm,:em,:eo)',
                        db=db,values = {':s':r['start_frame'],
                                         ':e':r['end_frame'],
                                         ':sm':sm,
                                         ':em':em,
                                         ':eo':r['offset']})            
        db.commit()
        self.select()        
        
    # array of [[m,o]] ordered by distance
    def locate(self,row:int,pt:QgsPointXY,corrected:bool, maxOffset:float = 10.0, outsideRunDistance:float = 50.0)->np.array:
        minM,maxM = self.chainageRange(row,additional = outsideRunDistance)
        opt = self.gpsModel.locate(pt, minM = minM, maxM = maxM)#nearest within range.
        
        #outside maxDist
        if abs(opt[1]) > maxOffset:
            m = r'Could not find (chainage,offset) within {d}m of point and between {minM}m(frame{minF}) and {maxM}m(frame{maxF}). Check start/end frames and GPS data.'
            m = m.format(d = maxOffset,minF = mToFrame(minM) , maxF = mToFrame(maxM),maxM = maxM,minM = minM)
            raise ValueError(m)
            
        opts = np.array([opt])
    
        #if corrected and len(opts) > 0:
       #     opts[:,0] = opts[:,0] - self.index(row,self.fieldIndex('chainage_shift')).data()
       #     opts[:,1] = opts[:,1] - self.index(row,self.fieldIndex('offset')).data()
        return opts
        
        
    def saveCsv(self,file:str):
        with open(file,'w',newline='') as f:
            writer = csv.writer(f,dialect='excel',delimiter = '\t')
            writer.writerow(('start_frame','end_frame','chainage_shift','offset'))
            q = runQuery('select start_frame,end_frame,chainage_shift,offset from runs_view order by number')
            while q.next():
                writer.writerow((q.value(0),q.value(1),q.value(2),q.value(3)))
            
        
    def chainageRange(self,row:int,additional:float = 20.0)->Tuple[float,float]:
        startFrame = int(self.index(row,self.fieldIndex('start_frame')).data())
        endFrame = int(self.index(row,self.fieldIndex('end_frame')).data())
        return (frameToM(startFrame) - additional , frameToM(endFrame) + additional)
        
    
    #array -> array
    @staticmethod
    def correctMO(mo):
        q = prepareQuery('select chainage_shift,offset from runs_view where start_frame <= :f and end_frame >= :f order by start_frame limit 1')
        r = np.empty((len(mo),2),dtype = float) * np.nan
        for i,row in enumerate(mo):
            q.bindValue(':f',int(mToFrame(row[0])))
            if not q.exec():
                raise queryError(q)
            while q.next():
                r[i,0] = mo[i,0] + q.value(0)
                r[i,1] = mo[i,1] + q.value(1)
        return r
        
    
    
    #array -> array
    @staticmethod
    def unCorrectMO(mo):
        q = prepareQuery('select chainage_shift,offset from runs_view where start_frame <= :f and end_frame >= :f order by start_frame limit 1')
        r = np.empty((len(mo),2),dtype = float) * np.nan
        for i,row in enumerate(mo):
            q.bindValue(':f',int(mToFrame(row[0])))
            if not q.exec():
                raise queryError(q)
            while q.next():
                r[i,0] = mo[i,0] - q.value(0)
                r[i,1] = mo[i,1] - q.value(1)
        return r
        
    
    
    
    