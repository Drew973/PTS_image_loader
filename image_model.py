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
from image_loader import run_commands
from image_loader import layer_functions


#from qgis.core import QgsCoordinateReferenceSystem


#combobox current index changes. when rowCount changes...


from image_loader.runs_model import runsModel
from image_loader.gps_model import gpsModel


from collections import namedtuple


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




class imageModel(QSqlQueryModel,gpsModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
     #   self._db = db
        self.run = None
        self.runsModel = runsModel()
        self.runsModel.select()
        #self.gpsModel = gpsModel()
        self.setRun('')
        
    
    def save(self,file):
        db_functions.saveToFile(file)
        
        
    def load(self,file):
        db_functions.loadFile(file)
        self.select()
    
    
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
        t = self.query().lastQuery()#str
      #  print(t)
        self.setQuery(t,self.database())
       #self.setQuery(self.query()) query does not update model. bug in qt?
        self.runsModel.select()
       
        
    def clear(self):
        q = QSqlQuery(self.database())
        if not q.exec('delete from images'):
            raise db_functions.queryError(q)
            
        gpsModel.clear(self)
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
        
                
    '''
    some inaccuracy
    offsetCurve
    '''
    #load images into qgis
    def georeference(self,indexes=None):
        #print('georeference')
       # progress = createProgressDialog(parent=self.parent(),labelText = "Calculating positions...")
        
        progress = run_commands.commandRunner(parent=self.parent(),labelText = "Calculating positions...")
        progress.setAutoClose(False)
        progress.show()
        
        georeferenceCommands = []
        sources = []
        q = db_functions.runQuery('select original_file,st_asText(left_line),st_asText(right_line) from images_view')
      #  q = db_functions.runQuery('select original_file,start_m,end_m,left_offset,right_offset from images_with_correction')
        while q.next():
            file = q.value(0)#string
          #  left = query.value(1)#QVariant
          #  right = query.value(2)#QVariant

            if os.path.exists(file):
                #left = self.gpsModel.getLine(startM = q.value(1),endM = q.value(2),offset=q.value(3))               
                #right = self.gpsModel.getLine(startM = q.value(1),endM = q.value(2),offset=q.value(4))
                sources.append(georeference.warpedFileName(file))
                left = q.value(1)
                right = q.value(2)
               # print('left',left)
              #  print('right',right)
                c = 'python "{script}" "{file}" "{left}" "{right}"'.format(script = georeference.__file__,file = file, left = left,right=right)
                georeferenceCommands.append(c)

        if georeferenceCommands:
            progress.setLabelText('removing layers...')
            layer_functions.removeSources(sources)#remove layers to allow file to be edited.
            
           # print(georeferenceCommands[0])
            progress.setLabelText('writing files...')
            progress.setAutoClose(True)
            progress.runCommands(commands = georeferenceCommands)#running in paralell.
            progress.exec()

            
       # print(georeferenceCommands)
       # progress.close()#close immediatly otherwise haunted by ghostly progressbar
    ##    progress.deleteLater()
     #   del progress    
    
   
    '''
    unused. probabaly unnecessary. Strange behavior creating overviews for vrt. No external file created but line like 
    <OverviewList>2 4 8 16 32 64 </OverviewList>
    added to band.
    overview exists in memory?
    
    '''
    def createOverviews(self):
        progress = run_commands.commandRunner(parent=self.parent(),labelText = "Calculating positions...")
        progress.setAutoClose(False)
        progress.show()
        
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
       # print(commands)
        progress.setAutoClose(True)
        progress.runCommands(commands = commands)#running in paralell.
        progress.exec()


    def makeVrt(self):
        vrtData = namedtuple('vrtData', ['files', 'vrtFile', 'tempFile','imageType','run'])
        
        progress = run_commands.commandRunner(parent=self.parent(),labelText = "fetching data...")
        progress.setAutoClose(False)
        progress.show()
        
        #use something unlikey to be in file name as seperator.
        query = db_functions.runQuery("select group_concat(original_file,'[,]'),run,image_type from images where marked group by run,image_type order by original_file")
        data = []
        while query.next():
            files = [os.path.normpath(georeference.warpedFileName(f)) for f in query.value(0).split('[,]') if os.path.isfile(georeference.warpedFileName(f))]
           # print(files)        
            if files:
                if os.path.isdir(self.fields['folder']):
                    destFolder = os.path.join(self.fields['folder'],'Combined Images',query.value(2))
                else:
                    destFolder = os.path.commonpath(files) 
                vrtFile = os.path.join(destFolder,
                                       '{tp}_{run}.vrt'.format(run = query.value(1),tp = query.value(2)))
                tempFile = vrtFile + '.txt'
                data.append(vrtData(files,vrtFile,tempFile,query.value(2),query.value(1)))
                
        progress.setLabelText('removing layers')
     #   print([v.vrtFile for v in data])
        layer_functions.removeSources([v.vrtFile for v in data])                
                
        progress.setLabelText('preparing...')        
        progress.setRange(0,len(data))
        
        buildCommands = []
        overviewCommands = []
        
        for i,v in enumerate(data):
            if progress.wasCanceled():
                return
            
            progress.setValue(i)
            
            vrtFile = v.vrtFile
           #create directory for vrt file if necessary
           
            if not os.path.isdir(os.path.dirname(v.vrtFile)):
                os.makedirs(os.path.dirname(v.vrtFile))
            
            with open(v.tempFile,'w') as tf:                
                tf.write('\n'.join(['{f}'.format(f=file) for file in v.files]))
            
            #remove overview if exists
            overview = v.vrtFile+'.ovr'
            if os.path.isfile(overview):
                os.remove(overview)
                
            buildCommands.append('gdalbuildvrt -input_file_list "{fl}" -overwrite "{f}"'.format(fl = v.tempFile,f=v.vrtFile))
            c = 'gdaladdo -ro "{vrtFile}" 64,128,256,512 --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL'.format(vrtFile = v.vrtFile)
            
            overviewCommands.append(c)

        #print(buildCommands)
        progress.setLabelText('Writing VRT files...')
        progress.setAutoClose(True)
        progress.runCommands(commands = buildCommands)#running in paralell.
        progress.exec()

        progress.setLabelText('Creating overviews...')
     #   print(overviewCommands)
        progress.runCommands(commands=overviewCommands)   
        progress.exec()

        progress.show()
        progress.setLabelText('Loading results...')
        for v in data:
            #os.remove(data[vrtFile][0])
            
            groups = ['image_loader',
                       'combined VRT',
                       v.imageType,
                       v.run
                       ]
            loadImage(file = v.vrtFile,groups=groups)
            os.remove(v.tempFile)
    
    
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
        
        
    def unmarkAll(self):
        db_functions.runQuery(query = 'update images set marked=False')
        self.select()
        
        
    def markRun(self):
        #print('run',self.run)
        #db_functions.runQuery(query = "update images set marked = True where run = ':run'".replace(':run',self.run))#error when binding value?
        db_functions.runQuery(query = "update images set marked = True where run = :run",values = {':run':self.run})#not run when binding value. why?
        self.select()


    def unmarkRun(self):
       # print(self.run)
        db_functions.runQuery(query = "update images set marked = False where run = ':run'".replace(':run',self.run))#error when binding value?
        self.select()


    def markBetween(self,runIndex,start,end):
        pass    
    