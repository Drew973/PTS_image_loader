# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:25:12 2022

@author: Drew.Bennett

items have:
filePath: absolute path. doesn't need to be unique. when loading csv allow directory with csv + relative path
groups: list of groups. loaded to image_loader.groups[0].groups[1]...
run
image_id

combination of run and image_id should be unique

"""

from PyQt5.QtCore import Qt

import csv
import os

#import sqlite3
from PyQt5.QtSql import QSqlDatabase,QSqlQuery,QSqlTableModel

from image_loader import generate_details,load_layer,group_functions


dbFile = ":memory:"
#dbFile = r"C:\Users\drew.bennett\Documents\mfv_images\test\test_db.db"


class imageLoaderError(Exception):
    pass

     
class imageLoaderQueryError(Exception):
    def __init__(self,q):
        message = 'query "%s" failed with "%s"'%(q.lastQuery(),q.lastError().databaseText())
        super().__init__(message)




class imageModel(QSqlTableModel):
    
    
    def __init__(self,parent=None):
        
        db = QSqlDatabase.addDatabase('QSQLITE')   #QSqlDatabase
        db.setDatabaseName(dbFile)
        if not db.open():
            raise imageLoaderError('could not create database')
    
    
        self.createTable()
    
        super().__init__(parent,db)
        
        self.setTable('image_details')
        
    
    
    def createTable(self):
       # self.db 
        createTableQuery = QSqlQuery()
        createTableQuery.exec(
            '''
            CREATE TABLE image_details (
                pk integer primary key,
                run varchar NOT NULL,
                image_id int NOT NULL,
                file_path VARCHAR NOT NULL,
                name varchar,
                groups varchar
                

            )
            '''
        )
    
    def clearTable(self):
        query = 'delete from image_details'
        
        q = QSqlQuery(self.database())
        
        if not q.prepare(query):
            raise imageLoaderQueryError(q)    
        
        q.exec()
        self.select()
    
    
    #load images where run=run and startId<=imageId and imageId<=end_id
    def loadImages(self,run=None,startId=None,endId=None,hide=True):
#        print('loadImages({run}{startId}{endId})'.format(run=run,startId=startId,endId=endId))
        query = 'select file_path,name,groups from image_details'
        
        conditions = []
        
        if not run is None:
            conditions.append('run = :run')
   
        if not startId is None:
            conditions.append('image_id >= :start_id')
            
        if not endId is None:
            conditions.append('image_id <= :end_id')
        
        
        if conditions:
            query+= ' where '
            query += ' and '.join(conditions)
        
        
        q = QSqlQuery(self.database())
        
        if not q.prepare(query):
            raise imageLoaderQueryError(q)
        
        
        if not run is None:
            q.bindValue(':run',run)
   
        if not startId is None:
            q.bindValue(':start_id',startId)
            
        if not endId is None:
            q.bindValue(':end_id',endId)        
        
        q.exec()
        
        while q.next():
            filePath = q.value('file_path')
            name = q.value('name')
            g = group_functions.groupStringToList(q.value('groups'))
            
            load_layer.loadLayer(filePath,name,g,hide)
    
    
#load csv. converts all paths to absolute
    def loadCsv(self,file):
        with open(file,'r',encoding='utf-8-sig') as f:
            
            folder = os.path.dirname(file)
            reader = csv.DictReader(f)
            for r in reader:
                #convert paths to absolute
                if not os.path.isabs(r['file_path']):
                    filePath = os.path.join(folder,r['file_path'])
                else:
                    filePath = r['file_path']
                
                self.addRow(r['run'],r['image_id'],filePath,r['name'],r['groups'])


    #not working- no rows inserted or error raised. performance probably not important here...
    def addDataBatch(self,data):
        
        self.database().transaction()
        
        runs,image_ids,file_paths,groups = zip(*[(r['run'], r['image_id'],r['file_path'],r['groups']) for r in data])

        q = QSqlQuery(self.database())
        print(q.prepare("insert into image_details values (:run,:image_id,:file_path,:group);"))

        q.bindValue(':run',runs)
        q.bindValue(':image_id',image_ids)
        q.bindValue(':file_path',file_paths)
        q.bindValue(':group',groups)

        print('bound values:',q.boundValues())

        if not q.execBatch():
            raise imageLoaderQueryError(q)

        print(q.executedQuery())
        
        self.database().commit()
        self.select()


    def addData(self,data):
        for r in data:
            self.addRow(r['run'],r['image_id'],r['file_path'],r['name'],r['groups'])
    
    
    #groups:string
    def addRow(self,run,imageId,filePath,name,groups):
        q = QSqlQuery(self.database())
        if not q.prepare("insert into image_details(run,image_id,file_path,name,groups) values (:run,:image_id,:file_path,:name,:groups);"):
            raise imageLoaderQueryError(q)
            
        q.bindValue(':run',run)
        q.bindValue(':image_id',imageId)
        q.bindValue(':file_path',filePath)
        q.bindValue(':name',name)
        q.bindValue(':groups',groups)
        
        if not q.exec():
            print(run,imageId,filePath,name,groups)
            raise imageLoaderQueryError(q)

        self.select()


    #generate from folder structure
    def fromFolder(self,folder):
        self.addData(generate_details.generateDetails(folder))
    
    
    def header(self):
        return [self.headerData(i,Qt.Horizontal) for i in range(0,self.columnCount())]
  
    
    def row(self,row):
        return [self.index(row,i).data() for i in range(0,self.columnCount())]
  
    
    #write csv
    #converts all paths to relative
    def saveAsCsv(self,file):
       
        folder = os.path.dirname(file) 
        pathCol = self.fieldIndex('file_path')
        
        with open(file,'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(self.header())
            for i in range(0,self.rowCount()):
                row = self.row(i)
                row[pathCol] = os.path.relpath(row[pathCol],folder)#save relative path from csv folder
                w.writerow(row)
    
    
    #get list of runs
    def runs(self):
        
        q = self.preparedQuery('select distinct run from image_details')
        q.exec()
        
        while q.next():
            yield q.value('run')
           
            
           
    #returns QSqlQuery
    def preparedQuery(self,text):
        query = QSqlQuery(self.database())
        if not query.prepare(text):
            raise imageLoaderQueryError(query)
        return query
        
    
    
    #get max image id
    def maxId(self):
        q = self.preparedQuery('select max(image_id) as m from image_details')

        q.exec()
        
        while q.next():
            v = q.value('m')
            if isinstance(v,int):
                return v
            else:
                return 0
        
        
    
    #get min image id
    def minId(self):
        
        q = self.preparedQuery('select min(image_id) as m from image_details')
        q.exec()
        
        while q.next():
            v = q.value('m')
            if isinstance(v,int):
                return v
            else:
                return 0
        
