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
from image_loader.models.details import image_details

import logging
logger = logging.getLogger(__name__)
from image_loader.functions.setup_database import runQuery



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
        


    def loadCsv(self,file):
        logger.debug('loadCsv({})'.format(file))

        self.addData(image_details.fromCsv(file))
    
        
            
    def addData(self,data):
        logger.debug('addData')

        def groupsToText(groups):
            if isinstance(groups,list):
                return json.dumps(groups)
            else:
                return groups
        
        if data:
            q = QSqlQuery(self.database())
            if not q.prepare("insert into details(run,image_id,file_path,name,groups) values (:run,:id,:file_path,:name,:groups);"):#ST_GeomFromWKB(:geom)
                raise exceptions.imageLoaderQueryError(q)
   
            data = [d for d in data]#make generator into list. end up going through it multiple times otherwise
    
            q.bindValue(':run',[d['run'] for d in data])
            q.bindValue(':id',[QVariant(d['imageId']) for d in data])
            q.bindValue(':file_path',[d['filePath'] for d in data])
            q.bindValue(':name', [d['name'] for d in data])
            q.bindValue(':groups', [groupsToText(d['groups']) for d in data])
         #   q.bindValue(':geom',[d['extents'] for d in data])
           
            logger.debug(q.boundValues())# crash if different lengths
    
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
        self.addData(image_details.fromFolder(folder))
                   
        
    #list of image_details corresponding to from selected features of layer
    def detailsFromSelectedFeatures(self,layer,fileNameField,idField):
        
        r = []
        q = QSqlQuery(self.database())
        
        #e = re.compile('MFV\S*\s ')# MFV, non space,space

        
        if not q.prepare('select file_path,name,groups from image_details where run=:run and image_id=:imageId'):
            raise exceptions.imageLoaderQueryError(q)
            
        
        for f in layer.selectedFeatures():
            #v = e.search(f[fileNameField])
            #if v:
            run = f['run'] 
            if run:                
                q.bindValue(':run',run)
                q.bindValue(':imageId',f[idField])
                q.exec()
                
                while q.next():
                    d = image_details.imageDetails(filePath = q.value('file_path'),
                              run = q.value('run'),
                              imageId = q.value('image_id'),
                              name = q.value('image_id'),
                              groups = json.loads(q.value('groups')))
                    
                    r.append(d)
        return r
    
    
  
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
        
    
