# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:55:49 2023

@author: Drew.Bennett



create database and tables in db_functions.createDb().

"""

from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase

import os
import csv
#import re


from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog

import glob


from image_loader import db_functions
from image_loader.name_functions import generateRun,generateImageId,findOrigonals,generateImageType
from image_loader.load_image import loadImage
#from image_loader import gdal_commands
from image_loader import georeference
from image_loader.run_commands import runCommands



#from qgis.core import QgsCoordinateReferenceSystem

from osgeo import gdal

#combobox current index changes. when rowCount changes...


from image_loader.runs_model import runsModel




class _image():
    
    def __init__(self,imageId = None ,origonalFile = '',newFile = '',run = ''):
        
        f = ''
        if origonalFile:
            f = origonalFile
        else:
            if newFile:
                f = newFile
        
        if imageId is None:
            self.imageId = generateImageId(f)
        else:
            self.imageId = imageId
            
            
        self.origonalFile = origonalFile
        self.newFile = newFile
        
        if run:
            self.run = run
        else:
            self.run = generateRun(f)

        self.imageType = generateImageType(f)
        



def createProgressDialog(parent=None,labelText=''):
        progress = QProgressDialog(labelText,"Cancel", 0, 0,parent=parent)#QObjectwithout parent gets deleted like normal python object
        progress.setWindowModality(Qt.WindowModal)
        progress.setAutoClose(False)
        progress.show()
        progress.forceShow()    
        return progress




class imageModel(QSqlQueryModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
     #   self._db = db
        self.run = None
        self.runsModel = runsModel()
        self.runsModel.select()
        self.setRun('')
        
    
    def fieldIndex(self,name):
        return self.record().indexOf(name)
        
    
    
    def data(self,index,role = Qt.EditRole):
        if role == Qt.BackgroundColorRole:
            if self.index(index.row(),self.fieldIndex('marked')).data(Qt.EditRole):
                return QColor('yellow')
            else:
                return QColor('white')

        #special handling for marked column
        if index.column() == self.fieldIndex('marked'):
        
            if role == Qt.EditRole:
                return bool(super().data(index,role))

            if role == Qt.DisplayRole:
                return None

            if role == Qt.CheckStateRole:
                if super().data(index,Qt.EditRole):
                    return Qt.Checked
                else:
                    return Qt.Unchecked

        return super().data(index,role)
        
    
    def setData(self,index,value,role = Qt.EditRole):
     #   print('role',role)#Qt.EditRole when editing through delegate
   #     print('value',value)
        if index.column() == self.fieldIndex('marked'):
            if role == Qt.EditRole:
            #    print(value)
                self.mark([index],value)
        return True
    
    #def flags(self,index):
      #  if index.column() == self.fieldIndex('marked'):
      #      return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
     #   else:
     #       return super().flags(index)
    
    def database(self):
        return QSqlDatabase.database('image_loader')


    def select(self):
        t = self.query().lastQuery()
        self.setQuery(t,self.database())
       #self.setQuery(self.query()) query does not update model. bug in qt?
        self.runsModel.select()
       
        
    def clear(self):
        q = QSqlQuery(self.database())
        if not q.exec('delete from images'):
            raise db_functions.queryError(q)
        self._refreshRuns()
        self.select()

    def _refreshRuns(self):
        oldRun = self.run
        self.runsModel.select()
        self.setRun(oldRun)
 
    def setRun(self,run):
        if str(run) != str(self.run):
            if run:
                filt = "where run = '{run}'".format(run=run)#"
            else:
                filt = ''
            q = 'select marked,pk,run,image_id,original_file,image_type from images {filt} order by image_id,original_file,image_type'.format(filt=filt)
            self.setQuery(q,self.database())
            self.run = run
        
        
    #load images into qgis
    def loadImages(self,indexes):
        progress = createProgressDialog(parent=self.parent(),labelText = "Loading images...")
        query = db_functions.runQuery('select original_file,run,image_type from images where marked and not original_file is null')
        progress.setRange(0,query.size())
        i = 0
        
        while query.next():
            
            if progress.wasCanceled():
                return
            progress.setValue(i)
            
            origonalFile = query.value(0)#string      
            warped = georeference.warpedFileName(origonalFile)

            if os.path.exists(warped):
                groups = ['image_loader',
                          query.value(2),
                          query.value(1)]
                loadImage(file=warped,groups=groups)
            i += 1
            
        progress.close()#close immediatly otherwise haunted by ghostly progressbar
        progress.deleteLater()
        del progress
        
    
    def hasGps(self):
        return db_functions.hasGps(self.database())
                
    
    #load images into qgis
    def georeference(self,indexes=None):
        #print('georeference')
        progress = createProgressDialog(parent=self.parent(),labelText = "Calculating positions...")
        georeferenceCommands = []
        query = db_functions.runQuery('select original_file,st_asText(left_line),st_asText(right_line) from images_view')
        
        while query.next():
            file = query.value(0)#string
            left = query.value(1)#QVariant
            right = query.value(2)#QVariant

            if os.path.exists(file):
                c = 'python "{script}" "{file}" "{left}" "{right}"'.format(script = georeference.__file__,file = file, left = left,right=right)
                georeferenceCommands.append(c)

        if georeferenceCommands:
            #print(georeferenceCommands)
            progress.setLabelText('writing files...')       
            runCommands(commands = georeferenceCommands,progress=progress)#running in paralell.
       # print(georeferenceCommands)
        progress.close()#close immediatly otherwise haunted by ghostly progressbar
        progress.deleteLater()
        del progress    
    
   
    '''
    unused. probabaly unnecessary. Strange behavior creating overviews for vrt. No external file created but line like 
    <OverviewList>2 4 8 16 32 64 </OverviewList>
    added to band.
    overview exists in memory?
    
    '''
    def createOverviews(self):
        progress = createProgressDialog(parent=self.parent(),labelText = "Creating overviews...")
        query = db_functions.runQuery('select original_file from images where marked')
        files = []
        while query.next():
            f = georeference.warpedFileName(query.value(0))
            if os.path.isfile(f):
                files.append(f)
        #print(files)
        #warpedFileName()
        template = 'gdaladdo "{file}" 2 4 8 16 32 64 --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL'
        commands = [template.format(file = f) for f in files]
        print(commands)
        runCommands(commands = commands,progress=progress)#running in paralell.
        progress.close()#close immediatly otherwise haunted by ghostly progressbar
        progress.deleteLater()
        del progress    


    def makeVrt(self):
        progress = createProgressDialog(parent=self.parent(),labelText = "Making VRT files...")        
        query = db_functions.runQuery("select group_concat(original_file,':'),run,image_type from images where marked group by run,image_type order by original_file")
        progress.setMaximum(query.size())
        while query.next():
                        
            if progress.wasCanceled():
                break
            
            files = []
            for f in query.value(0).split(':'):
                warped = georeference.warpedFileName(f)
                if os.path.isfile(warped):
                    files.append(warped)
                  
            if files:
                if os.path.isdir(self.fields['folder']):
                    folder = os.path.join(self.fields['folder'],'Combined Images',query.value(2))
                
                else:
                    folder = os.path.dirname(files[0])
                
                
                if not os.path.isdir(folder):
                    os.makedirs(folder)
                 
                vrtFile = os.path.join(folder,
                                       '{tp}_{run}.vrt'.format(run = query.value(1),tp = query.value(2)))        
                
                #print(vrtFile,files)

                dest = gdal.BuildVRT(vrtFile, files)
                
                #build overview for vrt.
                gdal.SetConfigOption("COMPRESS_OVERVIEW", "jpg")
                dest.BuildOverviews("AVERAGE", [32,64,128,256])
                dest.flushCache()
                dest = None
                
                groups = ['image_loader',
                          'combined VRT',
                          query.value(2),
                          query.value(1)]
                loadImage(file = vrtFile,groups=groups)              
                
            progress.setValue(progress.value()+1)
            
            
        progress.close()#close immediatly otherwise haunted by ghostly progressbar
        progress.deleteLater()
        del progress    
    
    
    def loadGps(self,file):
        db_functions.loadGps(file=file,db=self.database())
        
        
    
    def addFolder(self,folder):
        pattern = folder+'/**/*.jpg'
        self._add([_image(origonalFile = f) for f in glob.glob(pattern,recursive=True)])
    
    
    def dropRows(self,indexes):
        col = self.fieldIndex('pk')
        pks = [str(self.index(index.row(),col).data()) for index in indexes]
        q = 'delete from images where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        db_functions.runQuery(q)
        self.select()    
        self._refreshRuns()
    

    
    def loadFile(self,file):
        
        def _find(d,k):
            if k in d:
                return d[k]
        
        
        ext = os.path.splitext(file)[-1]
        if ext in ['.csv','.txt']:
        
            data = []
            
            with open(file,'r',encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                reader.fieldnames = [name.lower().replace('_','') for name in reader.fieldnames]#lower case keys/fieldnames                 
                for row in reader:
                    
        
                    p = row['filepath']
                    if os.path.isabs(p):
                        filePath = p
                    else:
                        filePath = os.path.normpath(os.path.join(file,p))#from file not folder
                          
                    data.append(_image(newFile = filePath,
                                run = _find(row,'runid'),
                                imageId= _find(row,'frameid')
                                ))

            #    print('dat',data)

            #find origonal files
            if 'Raster Image Load File' in file and os.path.isdir(self.fields['folder']):
                files = [im.newFile for im in data]
                
                origonalFiles = findOrigonals(files,projectFolder = self.fields['folder'])
               
                for i,f in enumerate(origonalFiles):
                    data[i].origonalFile = f
               
            self._add(data)
         
            
    def _add(self,data):
            
        self.database().transaction()
        
        q = QSqlQuery(self.database())
        if not q.prepare('insert into images(image_id,original_file,new_file,run,image_type) values(:i,:origonal,:new,:run,:type)'):
            raise db_functions.queryError(q)
            
            
        for d in data:
            
            q.bindValue(':i',d.imageId)
            q.bindValue(':origonal',d.origonalFile)
            q.bindValue(':new',d.newFile)
            q.bindValue(':run',d.run)
            q.bindValue(':type',d.imageType.name)

            if not q.exec():
                    print(q.boundValues())
                    raise db_functions.queryError(q)
            
        self.database().commit()
        self.select()
        #self._refreshRuns()



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
        #self._refreshRuns()
      
      
    def markAll(self):
        db_functions.runQuery(query = 'update images set marked=True')
        self.select()
        self._refreshRuns()
        
    def unmarkAll(self):
        db_functions.runQuery(query = 'update images set marked=False')
        self.select()
        #self._refreshRuns()
        
    def markBetween(self,runIndex,start,end):
        pass    
    