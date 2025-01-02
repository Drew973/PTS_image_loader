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
from qgis.core import QgsPointXY,QgsGeometry
import typing
from image_loader.dims import mToFrame,frameToM
from image_loader.db_functions import runQuery,defaultDb,prepareQuery,queryError
from image_loader.image_model import imageModel
from image_loader.type_conversions import asFloat
from image_loader import settings

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

#area in wgs84
def runFromArea(area : QgsGeometry , bearing : int):
    pass

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
    
    
class runsModel(QSqlQueryModel):
    
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
    def addRuns(self,runs:typing.Iterable[int]):
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
        
        

        
        
    #rename to loadStr
    #load text from excel via clipboard etc
    def loadText(self,text:str):
        f = io.StringIO('start_frame\tend_frame\tchainage_shift\toffset\n'+text)
        self.addRows(parseCsv(f))
    
    
    def loadCsv(self,file:str):
        with open(file,'r') as f:
            self.addRows(parseCsv(f),clear=True)
        
        
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
    #run should only pass near point once...
    def locate(self , row : int, x : float , y : float) -> np.array:
        outsideRunDistance = asFloat(settings.value('outsideRunDistance') , 50.0)
        minM = frameToM(int(self.index(row , self.fieldIndex('start_frame')).data())) - outsideRunDistance
        maxM = frameToM(int(self.index(row , self.fieldIndex('end_frame')).data())) + outsideRunDistance
        return self.gpsModel.locate(x = x , y = y , minM = minM , maxM = maxM )#nearest within range.



