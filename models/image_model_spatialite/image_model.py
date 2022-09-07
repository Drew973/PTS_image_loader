
from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase,QSqlTableModel
from PyQt5.QtCore import pyqtSignal,Qt,QVariant

import csv
import json
import logging
import os

from qgis.utils import iface

from image_loader import exceptions
from image_loader.functions.run_query import runQuery
from image_loader.models.details import image_details

logger = logging.getLogger(__name__)


 
#select load,run,image_id,file_path,name,groups,pk from details where 1=1 order by round(run),run,image_id runs in dbBrowser

class imageLoaderQueryError(Exception):
    def __init__(self,q):
        message = 'query "%s" failed with "%s"'%(q.lastQuery(),q.lastError().databaseText())
        super().__init__(message)



'''
    model to display details table
    and add+remove rows
    
    setupDb(file) function here as depends on if using geopackage or sqlite or...
    
    ogr can't open dataSource when already open in QSqlDatabase()
    
    
    setRuns(self,runs): filter to these runs.
    selectRun(self,run,start,end): set load to True for these
    deselectAll(self)
    selectRows(self,ids)
    addFiles(self,files)
    addFolder(self,folder)
    load(self)
    clearTable(self)
    
    
print(QSqlDatabase.database('image_loader').driver().hasFeature(QSqlDriver.QuerySize)) False.
rowCount is the number of rows currently cached on the client as Spatialite driver cant get query size

'''

class imageModel(QSqlTableModel):
   # dbChanged = pyqtSignal()#changes made to database


#can't do default for database because
#Python's default arguments are evaluated only once when the function is defined, not each time the function is called.

    def __init__(self,db,parent=None):
        
        super().__init__(parent=parent,db=db)   
        self.setTable('details')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setFilter('1=1 order by round(run),run,image_id')
        #self.setRuns([])       
        self.select()
        
        
        
    def setRun(self,run):
        self._run = run
        self.setFilter("run='{run}' order by image_id".format(run=run))
        self.select()
        
        
    def run(self):
        return self._run
        
 #   def select(self):
            #round() returns float made of any digits in text,0 if none
   #     self.setQuery(QSqlQuery('select load,run,image_id,file_path,name,groups,pk from details order by round(run),run,image_id',QSqlDatabase.database('image_loader')))


 #   def fieldIndex(self,name):
 #       return self.record().indexOf(name)

 #   def fieldName(self,i):
 #       return self.record().fieldName(i) 


  #  def database(self):
 #       return QSqlDatabase.database('image_loader')
        
        
    def setRuns(self,runs):
        #self._runs = runs
        self.setFilter('run in ({runs})'.format(runs = ','.join(runs)))
        
        
        
    def selectRun(self,run,start,end):
        q = QSqlQuery(self.database())
        q.prepare('update details set load=True where run=:run and :start<=image_id and image_id<=:end')
        q.bindValue(':run',run)
        q.bindValue(':start',start)
        q.bindValue(':end',end)
        q.exec()
        self.select()
    
    
    def clearTable(self):
        logger.debug('clearTable')
        query = 'delete from details'
        q = QSqlQuery(self.database())
        if not q.prepare(query):
            raise imageLoaderQueryError(q)    
        
        q.exec()
        self.select()
    

    #doing some type casting here as SQlite doesn't have strictly defined types.
    def data(self,index,role):
        #image_id supposed to be be int. SQlite doesn't realy have types.
        if index.column() == self.fieldIndex('image_id') and role == Qt.DisplayRole:
            return int(super().data(index,role))         
    
        if index.column() == self.fieldIndex('load'):
            if  role == Qt.CheckStateRole:
                if bool(super().data(index,Qt.DisplayRole)):
                    return Qt.Checked
                else:
                    return Qt.Unchecked
                
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return bool(super().data(index,role))
 
        return super().data(index,role)
    
    
    def pk(self,row):
        return self.index(row,self.fieldIndex('pk')).data()
    
    
   # def setData(self,index,value,role=Qt.EditRole):
        
    #    q = 'update details set {col} = :value where pk = :pk'.format(col = self.fieldName(index.column()))
                                                                                        
    #    pk = self.pk(index.row())
    #    print(pk)
    #    print(q) 
    #   runQuery(q,self.database(),{':pk':pk,':val':value})
     #   self.select()
     #   return True
    
    
    
    def flags(self,index):
        if index.column()==self.fieldIndex('load'):
          #  return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
            return super().flags(index) | Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        
        #prevent editing run column.
        if index.column()==self.fieldIndex('name'):
            return super().flags(index) | Qt.ItemIsEditable
        
        return super().flags(index) & ~Qt.ItemIsEditable



#list of details where selected in runs table
    def getDetails(self):
        q = '''select file_path,name,groups from details 
        where load'''
        
        query = runQuery(q,self.database())
        r = []
        
        while query.next():
            d = image_details.imageDetails(filePath = query.value('file_path'),
                      run = query.value('run'),
                      imageId = query.value('image_id'),
                      name = query.value('image_id'),
                      groups = json.loads(query.value('groups')))
            r.append(d)
        return r        
        

  
    def drop(self,pks):
        pks = [str(pk) for pk in pks]
        q = 'delete from details where pk in ({pks})'.format(pks=','.join(pks))
        runQuery(q,self.database())

        


#geomFromText seems to return null for any 3d geom.
    def addDetails(self,data):
        logger.debug('addData')

        def groupsToText(groups):
            if isinstance(groups,list):
                return json.dumps(groups)
            else:
                return groups
        
        if data:
            q = QSqlQuery(self.database())
            if not q.prepare("insert into details(load,run,image_id,file_path,name,groups,geom) values (False,:run,:id,:file_path,:name,:groups,GeomFromText(:geom,27700));"):#ST_GeomFromWKB(:geom)
                raise exceptions.imageLoaderQueryError(q)
       
            q.bindValue(':run',[d['run'] for d in data])
            q.bindValue(':id',[QVariant(d['imageId']) for d in data])
            q.bindValue(':file_path',[d['filePath'] for d in data])
            q.bindValue(':name', [d['name'] for d in data])
            q.bindValue(':groups', [groupsToText(d['groups']) for d in data])
            geoms = [d['wkt'] for d in data]
            q.bindValue(':geom',geoms)
           
            logger.debug(q.boundValues())# crash if different lengths
    
            #check lengths equal. crash if not.
            vals = q.boundValues()
            lengths = [len(vals[v]) for v in vals]
            
            if not all([L==lengths[0] for L in lengths]):
                raise ValueError('incorrect lengths')
    
            if not q.execBatch():
                raise exceptions.imageLoaderQueryError(q)
                

    #load as qgis layer
    def loadLayer(self):
        uri = self.database().databaseName()+'|layername=details'
        return iface.addVectorLayer(uri,'details','ogr')

    #write csv, converting file_paths to relative
    def saveAsCsv(self,file):
               
        with open(file,'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['filePath','runId','imageId','name','groups','wkt'])
            
            q = runQuery('select file_path,run,image_id,name,groups,AsText(geom) from details',self.database())
            
            cols = [1,2,3,4,5]#columns are 0 indexed.
            
            while q.next():
                w.writerow([os.path.relpath(q.value(0),file)] + [q.value(n) for n in cols])