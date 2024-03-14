# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 14:55:49 2023

@author: Drew.Bennett



create database and tables in db_functions.createDb().

"""

from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase

import os
import csv

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from image_loader import db_functions
from image_loader.name_functions import generateRun,generateImageId,findOrigonals,generateImageType,projectFolderFromRIL
from image_loader.load_image import loadImage
from image_loader import georeference
from image_loader import run_commands
from image_loader import layer_functions
from pathlib import Path


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
        progress.show()
        return progress



class imageModel(QSqlQueryModel):
    
    def __init__(self,parent=None):
        super().__init__(parent)
      #  self.setRange(0,99999999999999)
        self.select()

    def save(self,file):
        db_functions.saveToFile(file)
        
        
    def load(self,file):
        db_functions.loadFile(file)
        self.select()
    
    
    def fieldIndex(self,name):
        return self.record().indexOf(name)
    
    
    def data(self,index,role):
        if role == Qt.ToolTipRole:
            return str(super().data(index))
        return super().data(index,role)
    
    
    @staticmethod
        #load images into qgis
    def georeference(gpsModel,pks = [],progress = None):
       # print('pks',pks)
        if pks:

            georeferenceCommands = []
            sources = []
            pkStr = ','.join([str(pk) for pk in pks])
            t = 'select frame_id,group_concat(original_file) from images where pk in ({p}) group by frame_id order by frame_id'.format(p=pkStr)
            q = db_functions.runQuery(t)
            while q.next():
                frame = q.value(0)
                gcp = gpsModel.gcps(frame)
                if gcp is not None:
                    for f in q.value(1).split(','):
                        newFile = georeference.warpedFileName(f)
                        sources.append(newFile)
                        georeferenceCommands.append('python "{script}" "{original}" "{new}" "{gcps}"'.format(original = f,
                                                                                                             script = georeference.__file__,
                                                                                                             new = newFile,
                                                                                                             gcps = gcp
                                                                                                             ))
        #    progress.setLabelText('Unloading Tif files')
            layer_functions.removeSources(sources)#remove layers to allow file to be edited.
          
           #ramove VRT files containing images
         #   progress.setLabelText('Unloading VRT files')
            vrtFiles = []
            qs = 'select image_type,run,group_concat(original_file) from images_view where pk in ({pks}) and run is not null group by image_type,run'.format(pks = pkStr)
            q = db_functions.runQuery(qs)
            while q.next():
                vrtFiles.append(imageModel.vrtFile(q.value(1),q.value(0),str(q.value(2)).split(',')))
           # print('vrtFiles',vrtFiles)
            layer_functions.removeSources(vrtFiles)#remove layers to allow file to be edited.


       #     print('georeferenceCommands',georeferenceCommands)
            if georeferenceCommands:
                #print(georeferenceCommands[0])
                run_commands.runCommands(commands = georeferenceCommands,progress = progress)
   
    
    @staticmethod        
    def vrtFile(run,imageType,files):
        if len(files) ==1 :
            folder = os.path.dirname(files[0])
        else:
            folder = os.path.commonpath(files)
        return os.path.join(folder,'{tp}_{run}.vrt'.format(run = run,tp = imageType))
        
    
    
    def flags(self,index):
        if index.column() == self.fieldIndex('marked'):
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    
    def database(self):
        return QSqlDatabase.database('image_loader')


    def select(self):
        queryString = '''select pk,frame_id,original_file,image_type from images
            order by frame_id,image_type'''
        q = QSqlQuery(self.database())
        q.prepare(queryString)
        q.exec()
        self.setQuery(q)
        
     #   self.setRange()
      #  q = self.query()
      #  q.exec()
      #  self.setQuery(q)

        
    def clear(self):
        q = QSqlQuery(self.database())
        if not q.exec('delete from images'):
            raise db_functions.queryError(q)
        self.select()


    def setRange(self,start,end):
        #s = startChainage/HEIGHT
        #e = endChainage/HEIGHT
    #    print('setRange',s,e)        
        queryString = '''select pk,frame_id,original_file,image_type from images
            where :s <= frame_id and frame_id <= :e
            order by frame_id,image_type'''
        q = QSqlQuery(self.database())
        q.prepare(queryString)
        q.bindValue(':s',start)
        q.bindValue(':e',end)
        q.exec()
        self.setQuery(q)

  
    #load images into qgis
    def loadImages(self,pks = []):
        p = ','.join([str(pk) for pk in pks])
        progress = createProgressDialog(parent=self.parent(),labelText = "Loading images...")
        t = 'select original_file,run,image_type from images_view where pk in ({pks}) and not original_file is null'.format(pks = p)
      #  query = db_functions.runQuery('select original_file,run,image_type from images_view where marked and not original_file is null')
        query = db_functions.runQuery(t)
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
        
        

     
    @staticmethod
    def makeVrt(pks,progress,folder = ''):
        
        #use something unlikey to be in file name as seperator.
        p = ','.join([str(pk) for pk in pks])
        query = db_functions.runQuery("select group_concat(original_file,'[,]'),run,image_type from images_view where pk in ({pks}) group by run,image_type order by original_file".format(pks = p))
        
        d = {}
        buildCommands = []
        overviewCommands = []
        tempFiles = []
        
        while query.next():
            
            run = query.value(1)
            tp = query.value(2)
            
            # existing warped files
            files = [os.path.normpath(georeference.warpedFileName(f)) for f in query.value(0).split('[,]') if os.path.isfile(georeference.warpedFileName(f))]
           # print(files)
            if files:
                
                vrtFile = imageModel.vrtFile(run = run,imageType = tp, files = files)
                tempFile = vrtFile + '.txt'
                folder = os.path.dirname(vrtFile)
                #print('folder',folder)
                if not os.path.isdir(folder):
                    os.makedirs(folder)
                
                
                #write tempuary file to get around console charactor limit.
                tempFile = vrtFile + '.txt'
                with open(tempFile,'w') as tf:                
                    tf.write('\n'.join(['{f}'.format(f=file) for file in files]))
              
                tempFiles.append(tempFile)
                
                #remove overview if exists
            #    overview = vrtFile+'.ovr'
           #     if os.path.isfile(overview):
            #        os.remove(overview)
                
                buildCommands.append('gdalbuildvrt -input_file_list "{fl}" -overwrite "{f}"'.format(fl = tempFile,f=vrtFile))
               # overviewCommands.append('gdaladdo -ro "{vrtFile}" 32 64,128,256,512 --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL'.format(vrtFile = vrtFile))
                overviewCommands.append('gdaladdo -ro -clean "{vrtFile}" 32 64,128,256,512 --config COMPRESS_OVERVIEW JPEG --config INTERLEAVE_OVERVIEW PIXEL'.format(vrtFile = vrtFile))


#
                groups = ['image_loader', 'combined VRT', tp, run]
                d[vrtFile] = groups

    #    print('d',d)
        layer_functions.removeSources(d.keys())           
        run_commands.runCommands(commands = buildCommands , progress = progress)
        run_commands.runCommands(commands = overviewCommands , progress = progress)

        for tempFile in tempFiles:
            os.remove(tempFile)
        
        for k in d:
            loadImage(file = k,groups=d[k])



    def addFolder(self,folder):
        #pattern = folder+'/**/*.jpg'
       # pattern = folder+'/**/*.jpg'
        files = [str(f) for f in Path(folder).glob("**/*.jpg")]
    #    print('files',files)
        self._add([_image(origonalFile = str(f)) for f in files])
        #self._add([_image(origonalFile = f) for f in glob.glob(pattern,recursive=True)])
    
    
    def dropRows(self,indexes):
        col = self.fieldIndex('pk')
        pks = [str(self.index(index.row(),col).data()) for index in indexes]
        q = 'delete from images where pk in ({pks})'.format(pks = ','.join(pks))
        #print(q)
        db_functions.runQuery(q)
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
        db = self.database()
        db.transaction()
        q = QSqlQuery(db)
        if not q.prepare('insert or ignore into images(frame_id,original_file,image_type) values(:i,:origonal,:type)'):
            raise db_functions.queryError(q)
        for d in data:
            q.bindValue(':i',d.imageId)
            q.bindValue(':origonal',d.origonalFile)
            q.bindValue(':type',d.imageType.name)
            if not q.exec():
                    print(q.boundValues())
                    raise db_functions.queryError(q)
        db.commit()
        self.select()
        

    def saveAs(self,file):
        pass
