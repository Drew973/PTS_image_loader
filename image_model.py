# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:55:49 2023

@author: Drew.Bennett



create database and tables in db_functions.createDb().

"""

from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase

import os
import csv

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog

import glob

from image_loader import db_functions
from image_loader.name_functions import generateRun,generateImageId,findOrigonals,generateImageType,projectFolderFromRIL
from image_loader.load_image import loadImage
from image_loader import georeference
from image_loader import run_commands
from image_loader import layer_functions
from image_loader.runs_model import runsModel


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
        #progress.setAutoClose(False)
        progress.show()
     #   progress.forceShow()    
        return progress




class imageModel(QSqlQueryModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
     #   self._db = db
        self.run = None
        self.runsModel = runsModel()
        self.runsModel.select()
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
        self.setQuery(t,self.database())
       #self.setQuery(self.query()) query does not update model. bug in qt?
        self.runsModel.select()
       
        
    def clear(self):
        q = QSqlQuery(self.database())
        if not q.exec('delete from images'):
            raise db_functions.queryError(q)
            
        self.runsModel.clear()
        self.select()


   # def _refreshRuns(self):
       # self.runsModel.select()
        
    
    
    def setRun(self,run):
        if str(run) != str(self.run):
            if run is not None:
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
        db_functions.correctGps()
        georeferenceCommands = []
        sources = []
        q = db_functions.runQuery('select original_file,st_asText(center_line) from images_view')
        while q.next():
            file = q.value(0)#string
            if os.path.exists(file):
                sources.append(georeference.warpedFileName(file))
                c = 'python "{script}" "{file}" "{cl}"'.format(script = georeference.__file__,file = file, cl = q.value(1))
                georeferenceCommands.append(c)
        if georeferenceCommands:
            layer_functions.removeSources(sources)#remove layers to allow file to be edited.
            run_commands.runCommands(commands = georeferenceCommands,labelText = 'Writing files...')
     

    def makeVrt(self):
        vrtData = namedtuple('vrtData', ['files', 'vrtFile', 'tempFile','imageType','run'])
        progress = QProgressDialog("Preparing...","Cancel", 0, 1,parent = self.parent())#QObjectwithout parent gets deleted like normal python object

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
        progress.close()
      
        buildCommands = []
        overviewCommands = []
        
        for v in run_commands.updateProgress(listLike = data , labelText = 'Preparing...'):
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
            c = 'gdaladdo -ro "{vrtFile}" 32 64,128,256,512 --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL'.format(vrtFile = v.vrtFile)
            
            overviewCommands.append(c)

        run_commands.runCommands(commands = buildCommands , labelText = 'Writing VRT files...')
        run_commands.runCommands(commands = overviewCommands , labelText = 'Creating overviews...')

        for v in run_commands.updateProgress(listLike = data , labelText = 'Loading layers...'):
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
       # self._refreshRuns()
        
    
   # def imageCount(self,run):
        

    def setRunForItems(self,indexes,run):
       col = self.fieldIndex('pk')
       pks = [str(self.index(index.row(),col).data()) for index in indexes]
       q = "update images set run = ':run' where pk in ({pks})".format(pks = ','.join(pks))
       db_functions.runQuery(query = q,values={':run':run})
       self.select()
    
    
    
    def loadRIL(self,file):
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
                              #  imageId= _find(row,'frameid')#use file name. starts from 1 in RIL file
                                ))
            #find origonal files
            if 'Raster Image Load File' in file:
                if os.path.isdir(self.fields['folder']):
                    projectFolder = self.fields['folder']
                else:
                    projectFolder = projectFolderFromRIL(file)
                if os.path.isdir(projectFolder):
                    files = [im.newFile for im in data]
                    origonalFiles = findOrigonals(files,projectFolder = projectFolder)
                    for i,f in enumerate(origonalFiles):
                        data[i].origonalFile = f
            self._add(data)
         
            
    def _add(self,data):
        
       # print(data[0].run)
        db = self.database()
        db.transaction()
           
        #self.runsModel.addRuns([str(d.run) for d in data])
        
        q = QSqlQuery(db)
        if not q.prepare('insert into images(image_id,original_file,run,image_type) values(:i,:origonal,:run,:type)'):
            raise db_functions.queryError(q)
            
            
        for d in data:
            
            q.bindValue(':i',d.imageId)
            q.bindValue(':origonal',d.origonalFile)
         #   q.bindValue(':new',d.newFile)
            q.bindValue(':run',d.run)
            q.bindValue(':type',d.imageType.name)

            if not q.exec():
                    print(q.boundValues())
                    raise db_functions.queryError(q)
            
        db.commit()
        self.select()
      #  self._refreshRuns()



    def saveAs(self,file):
        pass


    #if run index in indexes set all in run.
    def mark(self,indexes,value = True):
        col = self.fieldIndex('pk')
        pks = [str(self.index(index.row(),col).data()) for index in indexes]
        q = 'update images set marked = {value} where pk in ({pks})'.format(pks = ','.join(pks),value = str(value))
        db_functions.runQuery(q)
        self.select()
      
      
    def markAll(self):
        db_functions.runQuery(query = 'update images set marked=True')
        self.select()
        
        
    def unmarkAll(self):
        db_functions.runQuery(query = 'update images set marked=False')
        self.select()
        
        
    def markRun(self):
        db_functions.runQuery(query = "update images set marked = True where run = :run",values = {':run':self.run})#not run when binding value. why?
        self.select()


    def unmarkRun(self):
        db_functions.runQuery(query = "update images set marked = False where run = ':run'".replace(':run',self.run))#error when binding value?
        self.select()


    def markBetween(self,runIndex,start,end):
        pass    
    