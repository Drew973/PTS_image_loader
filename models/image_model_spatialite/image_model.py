
from PyQt5.QtSql import QSqlQuery,QSqlDatabase,QSqlTableModel
from PyQt5.QtCore import pyqtSignal,Qt

import csv
import json
import os



from qgis.utils import iface
from qgis.core import Qgis


from image_loader import exceptions
from image_loader.functions.run_query import runQuery
from image_loader.models.details import image_details


 
#select load,run,image_id,file_path,name,groups,pk from details where 1=1 order by round(run),run,image_id runs in dbBrowser

class imageLoaderQueryError(Exception):
    def __init__(self,q):
        message = 'query "%s" failed with "%s"'%(q.lastQuery(),q.lastError().databaseText())
        super().__init__(message)



'''


    model to display details table. sqlite database in memory or on disk.
    save will copy to file.
    loadFile will clear image details table and then insert values from file.
    
    
    and add+remove rows
        
    ogr can't open dataSource when already open in QSqlDatabase()
    selectRun(self,run,start,end): set load to True for these
    deselectAll(self)
    selectRows(self,ids)
    addFiles(self,files)
    addFolder(self,folder)
    clearTable(self)
    
    
print(QSqlDatabase.database('image_loader').driver().hasFeature(QSqlDriver.QuerySize)) False.
rowCount is the number of rows currently cached on the client as Spatialite driver cant get query size




def save(self,f)

'''

class imageModel(QSqlTableModel):
    rowsChanged = pyqtSignal()#changes made to database


#can't do default for database because
#Python's default arguments are evaluated only once when the function is defined, not each time the function is called.

    def __init__(self,db,parent=None):
        
        super().__init__(parent=parent,db=db)   
        if not db.isOpen():
            raise ValueError('database not open')
        
        self.setTable('details')
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.setFilter('1=1 order by round(run),run,image_id')
        #self.setRuns([])       
        self.select()
        self.setLayers()
        
        
    def setRun(self,run):
        self._run = run
        self.setFilter("run='{run}' order by image_id".format(run=run))
        self.select()
        
        
    def run(self):
        return self._run
        
    
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
        self.rowsChanged.emit()

        


#raster image load file is .txt in csv format.
    def loadFile(self,file):        
        ext = os.path.splitext(file)[-1]
        if ext in ['.csv','.txt']:
            self.addDetails([d for d in image_details.fromCsv(file)])
            return True

      #  if ext in ['.db','.sqlite']:        
       #     self.clearTable()
      #      db = QSqlDatabase.addDatabase('QSPATIALITE','image_loader_new')
         #   db.setDatabaseName(file)
                
        iface.messageBar().pushMessage('{ext} file format not supported.'.format(ext=ext), level=Qgis.Critical) 
        return False
    
          #  try:
             #   db.open()
            #    runQuery("ATTACH DATABASE '{f}' AS other;".format(f=file),self.database())
            #    runQuery("create table details AS select * from other.details",db)

                #r = True

          #  except Exception as e:
           #     iface.messageBar().pushMessage("Error", "Could not save to database:{e}".format(e=str(e)), level=Qgis.Critical)
             #   r = False

        #    finally:
          #      db.close()
          #      return r




#progress is QProgressDialog
#finding extents is slow. other details is not.
    def addFolder(self,folder,progress=None):
        files = [f for f in image_details.getFiles(folder,['.tif'])]
        self.addDetails([image_details.imageDetails(f) for f in files],progress=progress)


    '''
    load list of details.
    '''
    def addDetails(self,details,progress=None):
        
        if progress is not None:
            progress.setMaximum(len(details))  
            
        db = self.database()
        db.transaction()#doing all inserts in 1 transaction good for performance

        q = QSqlQuery(db)
        if not q.prepare("insert into details(load,run,image_id,file_path,name,groups,geom) values (False,:run,:id,:file_path,:name,:groups,GeomFromText(:geom,27700));"):#ST_GeomFromWKB(:geom)
            raise exceptions.imageLoaderQueryError(q)
        
        for i,d in enumerate(details):
            
            q.bindValue(':run',d['run'])
            q.bindValue(':id',d['imageId'])
            q.bindValue(':file_path',d['filePath'])
            q.bindValue(':name',d['name'])
            q.bindValue(':groups',json.dumps(d['groups']))
            q.bindValue(':geom',d['wkt'])
            
            if progress is not None:
                progress.setValue(i)
                if progress.wasCanceled():
                    break      
            
            if not q.exec():
                raise exceptions.imageLoaderQueryError(q)
                
        db.commit()
        self.select()
        self.rowsChanged.emit()



    #load as qgis layer
    def loadLayer(self):
        uri = self.database().databaseName()+'|layername=details'
        return iface.addVectorLayer(uri,'details','ogr')


    #save to new/existing file,overwrite of existing
    def save(self,f):
        ext = os.path.splitext(f)[-1]
        
        if ext in ['.csv','.txt']:
            self.saveAsCsv(f)
            return True
        
        if ext in ['.db','.sqlite']:        
            return self.saveAsDb(f)
            
            
        iface.messageBar().pushMessage("Error", "Unknown format {e}".format(e=ext), level=Qgis.Critical)

        
    def saveAsDb(self,file):
        db = QSqlDatabase.addDatabase('QSPATIALITE','image_loader_new')
        db.setDatabaseName(file)
        try:
            db.open()
            runQuery("ATTACH DATABASE '{f}' AS other;".format(f=self.database().databaseName()),db)
            runQuery("drop table if exists details",db)
            runQuery("create table details AS select * from other.details",db)
            iface.messageBar().pushMessage("Image_loader", "Saved to database", level=Qgis.Info)
            r = True
            
        except Exception as e:
            iface.messageBar().pushMessage("Error", "Could not save to database:{e}".format(e=str(e)), level=Qgis.Critical)
            r = False
            
        finally:
            db.close()
            return r

    #write csv/txt, converting file_paths to relative if possible
    def saveAsCsv(self,file):
               
        with open(file,'w',newline='') as f:
            w = csv.writer(f)
            w.writerow(['filePath','runId','imageId','name','groups','wkt'])
            
            q = runQuery('select file_path,run,image_id,name,groups,AsText(geom) from details',self.database())
            
            cols = [1,2,3,4,5]#columns are 0 indexed.
            
            while q.next():
                #can't convert to relative path if on different drive.
                try:
                    p = os.path.relpath(q.value(0),file)
                except:
                    p = q.value(0)
                    
                w.writerow([p] + [q.value(n) for n in cols])
        iface.messageBar().pushMessage("Image_loader", "Saved to csv", level=Qgis.Info)

                
    #find row given imageId and runId. -1 if not found
    def findRow(self,imageId,runId):
        idField = self.fieldIndex('image_id')
        runField = self.fieldIndex('run')
        for r in range(self.rowCount()):
            if self.index(r,idField).data() == imageId and self.index(r,runField).data() == runId:
                return r
        return -1
        
                
    def selectedFeatureRows(self):
        rows = [] 
        framesLayer = self.layers()['framesLayer']
        idField = self.layers()['idField']
        runField = self.layers()['runField']
        if idField and runField and framesLayer is not None:
            for f in framesLayer.selectedFeatures():
                r = self.findRow(int(f[idField]),f[runField])
                if r!=-1:
                    rows.append(r)
        return rows
            
    
    def selectOnLayer(self,rows):
        pass
           
    #dict or dialog with __getitem__ to get widget values.
    #uses layers['framesLayer']
    def setLayers(self,layers={'framesLayer':None,'idField':None,'runField':None}):
        self._layers = layers
        
        
    def layers(self):
        return self._layers
                
