# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 15:25:12 2022

@author: Drew.Bennett


model containing info about which images to load.




    delete from runs
    insert into runs...
    simpler than triggers

#if all runs are numeric then sort numerically,
otherwise sort alphabetically


"""

import logging
logger = logging.getLogger(__name__)

#import sqlite3
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt

#from image_loader.functions.load_image import loadImage
import json
from image_loader.models.image_model import details

from image_loader.functions.setup_database import runQuery


def toFloat(v):
    try:
        return float(v)
    except:
        return 



class runsModel(QSqlTableModel):
    
    def __init__(self,db,parent=None):
        logger.debug('__init__')
        super().__init__(parent=parent,db=db)
        self.setTable('runs')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()
       
        
       
    #converting run to float bad idea because eg float(100_6) = 1006.0.
    def data(self,index,role=Qt.DisplayRole):
        #SQlite has weird/no types.
        if (role == Qt.DisplayRole or role == Qt.EditRole) and index.column() == self.fieldIndex('show'):
            return bool(super().data(index,role))    
        
        if  role == Qt.CheckStateRole and index.column() == self.fieldIndex('show'):
            if bool(super().data(index,Qt.DisplayRole)):
                return Qt.Checked
            else:
                return Qt.Unchecked
        
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('start_id'):
            return int(super().data(index,role))
 
        if role == Qt.DisplayRole and index.column() == self.fieldIndex('end_id'):
            return int(super().data(index,Qt.DisplayRole))
    
        return super().data(index,role)
        
        
        
    def flags(self,index):
        if index.column()==self.fieldIndex('show'):
          #  return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
            return super().flags(index) | Qt.ItemIsUserCheckable
        
        #prevent editing run column.
        if index.column()==self.fieldIndex('run'):
            return super().flags(index) & ~Qt.ItemIsEditable
        
        return super().flags(index)



    def maxValue(self,index):
        if index.column() == self.fieldIndex('start_id') or index.column() == self.fieldIndex('end_id'):
            run = index.sibling(index.row(),self.fieldIndex('run')).data()
            q = runQuery('select max(image_id) from image_details where run=:run',self.database(),{':run':run})
            q.first()
            return q.value(0)
        else:
            raise NotImplementedError
            
        
       
    def minValue(self,index):
         if index.column() == self.fieldIndex('start_id') or index.column() == self.fieldIndex('end_id'):
             run = index.sibling(index.row(),self.fieldIndex('run')).data()
             q = runQuery('select min(image_id) from image_details where run=:run',self.database(),{':run':run})
             q.first()
             return q.value(0)
         else:
            raise NotImplementedError  



    def select(self):
        q = 'delete from runs where not run in (select distinct run from image_details);'
        
        #logger.debug(q)
        runQuery(q,self.database())

        q = '''insert or ignore into runs(run,start_id,end_id)
        select run,min(image_id),max(image_id) from image_details 
        group by run;
        '''
        #logger.debug(q)
        runQuery(q,self.database())
        
        super().select()
        
        

    def selectAll(self):
        q = 'update runs set show=True;'
        runQuery(q,self.database())
        self.select()


    def framesLayer(self):
        if self.parent() is not None:
            return self.parent().framesLayer()
    

    def idField(self):
        if self.parent() is not None:
            return self.parent().idField()

    
    def clearTable(self):
        runQuery('delete from runs',self.database())
        self.select()



#list of details where selected in runs table
    def getDetails(self):
        q = '''select file_path,name,groups from runs inner join image_details 
        on show=True and start_id<=image_id and image_id<=end_id and runs.run=image_details.run'''
        
        query = runQuery(q,self.database())
        r = []
        
        while query.next():
            d = details.imageDetails(filePath = query.value('file_path'),
                      run = query.value('run'),
                      imageId = query.value('image_id'),
                      name = query.value('image_id'),
                      groups = json.loads(query.value('groups')))
            r.append(d)
        return r




    def idFromFeatures(self,index):
        layer = self.framesLayer()
        field = self.idField()
        run = index.sibling(index.row(),self.fieldIndex('run')).data()
        print(run)
        if layer is not None and field is not None:
            ids = [int(f[field]) for f in layer.selectedFeatures() if f['run']==run]
            print(ids)
            if ids:
                if index.column()==self.fieldIndex('start_id'):
                    return min(ids)
                if index.column()==self.fieldIndex('end_id'):
                    return max(ids)                 


    def setFromFeatures(self,index):
        i = self.idFromFeatures(index)
        if i is not None:
            self.setData(index,i)
              