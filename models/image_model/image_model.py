# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:25:12 2022

@author: Drew.Bennett


model containg details to load each image.


items have:
filePath: absolute path. doesn't need to be unique. when loading csv allow directory with csv + relative path
groups: list of groups. loaded to image_loader.groups[0].groups[1]...
run
image_id

combination of run and image_id should be unique

"""

import csv
import os
import json

#import sqlite3
from PyQt5.QtSql import QSqlQuery,QSqlTableModel
from PyQt5.QtCore import pyqtSignal,Qt,QVariant

from image_loader import exceptions
from image_loader.models.image_model import details

import logging
logger = logging.getLogger(__name__)



class imageModel(QSqlTableModel):
    
    dbChanged = pyqtSignal()#changes made to database
    
    
    #dbFile can be ":memory:" or absolute path eg= r"C:\Users\drew.bennett\Documents\mfv_images\test\test_db.db"

    #
    def __init__(self,db,parent=None):
        
        super().__init__(parent=parent,db=db)   
        self.setTable('image_details')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setSort(self.fieldIndex('run'),Qt.AscendingOrder)
        self.select()
        
        
        
    def clearTable(self):
        
        logger.debug('clearTable')

        query = 'delete from image_details'
        
        q = QSqlQuery(self.database())
        
        if not q.prepare(query):
            raise exceptions.imageLoaderQueryError(q)    
        
        q.exec()
        self.select()
        self.dbChanged.emit()
        
        

    def details(self):
        q = '''select file_path,name,groups from runs inner join image_details 
        on show=True and start_id<=image_id and image_id<=end_id and runs.run=image_details.run'''
        
        query = runQuery(q,self.database())
       
        while query.next():
            yield details.imageDetails(filePath = query.value('file_path'),
                                       run = query.value('run'),
                                       imageId = query.value('image_id'),
                                       name = query.value('image_id'),
                                       groups = query.value('groups'))



    def loadCsv(self,file):
        logger.debug('loadCsv({})'.format(file))

        self.addData(details.fromCsv(file))
    
    
    
    #groups:string
    #only intended to be called through addData.
    def _addRow(self,filePath,run=None,imageId=None,name=None,groups=None,wkb=None):
        logger.debug('addRow')

        if isinstance(groups,list):
            groups = json.dumps(groups)
        
        
        q = QSqlQuery(self.database())
        if not q.prepare("insert into image_details(run,image_id,file_path,name,groups,geom) values (:run,:image_id,:file_path,:name,:groups,ST_GeomFromWKB(:geom));"):
            raise exceptions.imageLoaderQueryError(q)
            
        q.bindValue(':run',run)
        q.bindValue(':image_id',int(imageId))
        q.bindValue(':file_path',filePath)
        q.bindValue(':name',name)
        q.bindValue(':groups',groups)
        q.bindValue(':geom',wkb)

        if not q.exec():
            print(run,imageId,filePath,name,groups)
            raise exceptions.imageLoaderQueryError(q)

        
            
    def addData(self,data):
        logger.debug('addData')

        def groupsToText(groups):
            if isinstance(groups,list):
                return json.dumps(groups)
            else:
                return groups
        
        if data:
        
            #for d in data:
            #    self._addRow(d['filePath'],d['run'],d['imageId'],d['name'],d['groups'],d['extents'])
            q = QSqlQuery(self.database())
            if not q.prepare("insert into image_details(run,image_id,file_path,name,groups) values (:run,:id,:file_path,:name,:groups);"):#ST_GeomFromWKB(:geom)
                raise exceptions.imageLoaderQueryError(q)
    
   
            data = [d for d in data]#make generator into list. end up going through it multiple times otherwise
    
    
            q.bindValue(':run',[d['run'] for d in data])
            q.bindValue(':id',[QVariant(d['imageId']) for d in data])
            q.bindValue(':file_path',[d['filePath'] for d in data])
            q.bindValue(':name', [d['name'] for d in data])
            q.bindValue(':groups', [groupsToText(d['groups']) for d in data])
         #   q.bindValue(':geom',[d['extents'] for d in data])
           
            #print('query.isValid:',q.isValid())
            logger.debug(q.boundValues())# crash if different lengths
            #print(q.boundValues())# crash if different lengths
    
            #check lengths equal. crash if not.
            vals = q.boundValues()
            lengths = [len(vals[v]) for v in vals]
            
            if not all([L==lengths[0] for L in lengths]):
                raise ValueError('incorrect lengths')
    
            if not q.execBatch():
                raise exceptions.imageLoaderQueryError(q)
                
            self.select()
            self.dbChanged.emit()



    #generate from folder structure
    def fromFolder(self,folder):
        self.clearTable()
        self.addData(details.fromFolder(folder))
                   
    
  
    #write csv, converting file_paths to relative
    def saveAsCsv(self,file):
               
        with open(file,'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['filePath','runId','imageId','name','groups'])
            
            q = runQuery('select file_path,run,image_id,name,groups from image_details',self.database())
            
            cols = [1,2,3,4]#columns are 0 indexed.
            
            while q.next():
                w.writerow([os.path.relpath(q.value(0),file)] + [q.value(n) for n in cols])
    
    
    
    def data(self,index,role):
        #image_id supposed to be be int. SQlite doesn't realy have types.
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('image_id'):
            return int(super().data(index,role))         
    
        return super().data(index,role)
    
    
    
    def setData(self,index,value,role=Qt.EditRole):
        r = super().setData(index,value,role)
        self.dbChanged.emit()
        return r
        
    
    #checks query text and returns QSqlQuery
def preparedQuery(text,db):
    query = QSqlQuery(db)
    if not query.prepare(text):
        print(text)
        raise exceptions.imageLoaderQueryError(query)
    return query



#attempts to run query .Raise imageLoaderQueryError on failure.
def runQuery(text,db):
    q = preparedQuery(text,db)
    if not q.exec():
        raise exceptions.imageLoaderQueryError(q)
    return q
    


def createTable(db):
       q = '''
            CREATE TABLE if not exists image_details (
                pk integer primary key,
                run varchar NOT NULL,
                image_id int NOT NULL,
                file_path VARCHAR NOT NULL,
                name varchar,
                groups varchar
            )
            '''
       runQuery(q,db)
       
       #adding strict means proper type checking instead of dynamic types.
       #needs > version 3.37.0 (2021-11-27) for this
       
      #  "SELECT load_extension('mod_spatialite')",
 #"SELECT InitSpatialMetadata(1)",
 
     #  runQuery("SELECT load_extension('mod_spatialite')",db)
    #   runQuery("SELECT InitSpatialMetadata(1)",db)

 #      runQuery("SELECT AddGeometryColumn('image_details', 'geom', 27700, 'POLYGON')",db)
       
       
       