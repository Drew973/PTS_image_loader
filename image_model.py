# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:55:49 2023

@author: Drew.Bennett



create database and tables in db_functions.createDb().

"""

from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase
from image_loader import db_functions

import os
import csv
#import re


from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog

import glob

import numpy

from image_loader.name_functions import generateRun,generateImageId,findOrigonals,imageType
from image_loader.load_image import loadImage
from image_loader import gdal_commands


from qgis.core import QgsCoordinateReferenceSystem,QgsGeometry

class runsModel(QSqlQueryModel):
    
    def select(self):
        self.setQuery(QSqlQuery("SELECT distinct run from images order by run",db = self.database()))

    def database(self):
        return QSqlDatabase.database('image_loader')
    
    def allowedRange(self,index):
        return (0,999999)

    def crs(self,index):
        return QgsCoordinateReferenceSystem('EPSG:27700')

    def floatToPoints(self,index):
        pass






class imageModel(QSqlQueryModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
        db_functions.createDb()
        self.runsModel = runsModel()
        self.runsModel.select()
        self.setRun('')
        
    
    def fieldIndex(self,name):
        return self.record().indexOf(name)
        
    
    
    def data(self,index,role):
        if role == Qt.BackgroundColorRole:
            if self.index(index.row(),self.fieldIndex('marked')).data():
                return QColor('yellow')
            else:
                return QColor('white')

        else:
            return super().data(index,role)
        
    
    
    def database(self):
        return QSqlDatabase.database('image_loader')


    def select(self):
        t = self.query().lastQuery()
        self.setQuery(t,self.database())
       #self.setQuery(self.query()) query does not update model. bug in qt?
        
       
    def clear(self):
        q = QSqlQuery(self.database())
        if not q.exec('delete from images'):
            raise db_functions.queryError(q)
        self._refreshRuns()
        self.select()

    def _refreshRuns(self):
        #self.runsModel.setQuery(QSqlQuery("SELECT distinct run from images order by run",db = self.database()))
        self.runsModel.select()

 
    def setRun(self,run):
        if run:
            filt = "where run = '{run}'".format(run=run)#"
        else:
            filt = ''
        q = 'select pk,run,image_id,file,marked from images {filt} order by image_id,file'.format(filt=filt)
        self.setQuery(q,self.database())

        
    #load images into qgis
    def loadImages(self,indexes):
        
       # print(indexes)
        progress = QProgressDialog("Loading images...","Cancel", 0, 0,parent=self.parent())#QObjectwithout parent gets deleted like normal python object
        progress.setMinimumDuration(0)
        progress.setWindowModality(Qt.WindowModal)
        
       # print([index.row() for index in indexes])
        rows = numpy.unique([index.row() for index in indexes])
        fileCol = self.fieldIndex('file')
        runCol = self.fieldIndex('run')

        progress.setMaximum(len(rows))
        for i,row in enumerate(rows):
            if progress.wasCanceled():
                return
            
            progress.setValue(i)
            file = self.index(row,fileCol).data()
            
            groups = ['image_loader',
                      imageType(file).name,
                      self.index(row,runCol).data()]
            
            loadImage(file=file,groups=groups)
            
        progress.close()#close immediatly otherwise haunted by ghostly progressbar
        progress.deleteLater()
        del progress
        
        
        
    #load images into qgis
    def remakeImages(self,indexes):
        
        progress = QProgressDialog("Calculating locations...","Cancel", 0, 0,parent=self.parent())#QObjectwithout parent gets deleted like normal python object
        progress.setMinimumDuration(0)
        progress.setWindowModality(Qt.WindowModal)
        
        col = self.fieldIndex('pk')
        pks = [str(self.index(index.row(),col).data()) for index in indexes]
        
        db_functions.recalcChainages(pks)
        
        
        progress.setLabelText('Georeferencing images...')
        
        q = '''
        select file
        ,st_asText(Line_Substring(MakeLine(pt),(start_chainage-min(m))/(max(m)-min(m)),(end_chainage-min(m))/(max(m)-min(m)))) as line
        ,offset
        from 
        images left join
        (select pt,m,lead(m) over (order by m) as next_m,lag(m) over (order by m) as last_m from gps)g
        on 
        start_chainage<=next_m and end_chainage >= last_m
        and pk in (:pks)
        group by images.pk
        order by m
        '''
        
        query = db_functions.runQuery(query = q,values = {':pks':','.join(pks)})
        progress.setMaximum(len(pks))
        
        i = 0
        while query.next():
            
            if progress.wasCanceled():
                return
            progress.setValue(i)
            
            file = query.value(0)#string
            
            if hasattr(file,'value'):
                file = str(file.value())
            
            
            line = query.value(1)#QVariant
            
            
            if not isinstance(line,str):
                line = str(line.value())
            
            
            geom = QgsGeometry.fromWkt(line)
            print('file',file,'line',line,'geom',geom)
            
            c = gdal_commands.georeferenceCommand(file=file,geom=geom,offset = query.value(2))
            print(c)
            i += 1
            
            if i>len(pks):
                print('query returned more images whan expected')
                return
            
              
        progress.close()#close immediatly otherwise haunted by ghostly progressbar
        progress.deleteLater()
        del progress    
        
     
    
    '''
select 

*
--lc.start_chainage
,file
--,COALESCE(lc.end_offset-lc.start_offset,rc.end_offset-rc.start_offset,0)



--y  = c + mx
--x = start_chainage
--y = end_offset-start_offset
,COALESCE(
lc.end_offset-lc.start_offset + (a.ch-lc.start_chainage) * (rc.end_offset-rc.start_offset)/(rc.start_chainage-lc.end_chainage)
,lc.end_offset-lc.start_offset
,rc.end_offset-rc.start_offset
,0
)
as offset


--lc.end_offset-lc.start_offset as ly
--rc.end_offset-rc.start_offset as ry

from
(
select file
,image_id*5 as ch
--,image_id*5+5 as e_ch
--,start_chainage
--,end_chainage
,(select pk from corrections where start_chainage<=image_id*5 and corrections.run = images.run order by start_chainage desc limit 1) as left_correction
,(select pk from corrections where end_chainage>=image_id*5 and corrections.run = images.run order by start_chainage asc limit 1) as right_correction

from images
) a

left join corrections as lc on a.left_correction = lc.pk
left join corrections as rc on a.right_correction = rc.pk
    '''
    
   
    
    def loadGps(self,file):
        db_functions.loadGps(file=file,db=self.database())
        
        
    
    def addFolder(self,folder):
        pattern = folder+'/**/*.jpg'
        self._add( glob.glob(pattern,recursive=True))
    
    
    
    def dropRows(self,indexes):
        col = self.fieldIndex('pk')
        pks = [str(self.index(index.row(),col).data()) for index in indexes]
        q = 'delete from images where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        db_functions.runQuery(q)
        self.select()    
        self._refreshRuns()
    

    
    def loadFile(self,file):
        ext = os.path.splitext(file)[-1]
        if ext in ['.csv','.txt']:
                 #  self.addDetails([d for d in image_details.fromCsv(file)])
        
            files = []
            
            with open(file,'r',encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.lower().replace('_','') for name in reader.fieldnames]#lower case keys/fieldnames                 
                for d in reader:
                    p = d['filepath']
                    if os.path.isabs(p):
                        filePath = p
                    else:
                        filePath = os.path.normpath(os.path.join(file,p))#from file not folder
                                                
                    files.append(filePath)
                   # data.append([generateImageId(generateRun),generateRun(filePath),filePath])
                    
                   
            if 'Raster Image Load File' in file and os.path.isdir(self.fields['folder']):                   
                files = findOrigonals(files,projectFolder = self.fields['folder'])
            
            self._add(files)
            
            
            
    def _add(self,files):
        q = QSqlQuery(self.database())
        if not q.prepare('insert into images(image_id,file,run) values(:i,:f,:run)'):
            raise db_functions.queryError(q)
            
        for file in files:
            q.bindValue(':i',generateImageId(file))
            q.bindValue(':f',file)
            q.bindValue(':run',generateRun(file))

            if not q.exec():
                    print(q.boundValues())
                    raise db_functions.queryError(q)
            
        self.select()
        self._refreshRuns()



    def saveAs(self,file):
        pass


    #if run index in indexes set all in run.
    def mark(self,indexes,value = True):
        
        col = self.fieldIndex('pk')
        pks = [str(self.index(index.row(),col).data()) for index in indexes]
        q = 'update images set marked = {value} where pk in ({pks})'.format(pks = ','.join(pks),value = str(value))
        #print(q)
        db_functions.runQuery(q)
        
        self.select()
       # print(pks)
        
        
    def markBetween(self,runIndex,start,end):
        pass    
    
    

    
    