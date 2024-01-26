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
#from image_loader.runs_model import runsModel

#from image_loader.dims import WIDTH,PIXELS,LINES,HEIGHT
from collections import namedtuple
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
        self.setRange(0,99999999999999)
        
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
    def georeference(gpsModel,pks = []):
       # print('pks',pks)
        if pks:
            georeferenceCommands = []
            sources = []
            p = ','.join([str(pk) for pk in pks])
            t = 'select frame_id,group_concat(original_file) from images where pk in ({p}) group by frame_id order by frame_id'.format(p=p)
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
           # print('commands',georeferenceCommands)
            if georeferenceCommands:
                layer_functions.removeSources(sources)#remove layers to allow file to be edited.
                print(georeferenceCommands[0])
                run_commands.runCommands(commands = georeferenceCommands,labelText = 'Writing files...')


    def setData(self,index,value,role = Qt.EditRole):
        if index.column() == self.fieldIndex('marked'):
            if role == Qt.EditRole:
                self.mark([index],value)
        return True
    
    
    def flags(self,index):
        if index.column() == self.fieldIndex('marked'):
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
        else:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
    
    
    def database(self):
        return QSqlDatabase.database('image_loader')


    def select(self):
        q = self.query()
        q.exec()
        self.setQuery(q)

        
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
        
     

    def makeVrt(self,pks):
        
        
        vrtData = namedtuple('vrtData', ['files', 'vrtFile', 'tempFile','imageType','run'])
        progress = QProgressDialog("Preparing...","Cancel", 0, 1,parent = self.parent())#QObjectwithout parent gets deleted like normal python object

        #use something unlikey to be in file name as seperator.
        
        p = ','.join([str(pk) for pk in pks])
        query = db_functions.runQuery("select group_concat(original_file,'[,]'),run,image_type from images_view where pk in ({pks}) group by run,image_type order by original_file".format(pks = p))
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
                                       '{tp}_{run}.vrt'.format(run = str(query.value(1)),tp = query.value(2)))
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
        #pattern = folder+'/**/*.jpg'
       # pattern = folder+'/**/*.jpg'
        files = [str(f) for f in Path(folder).glob("**/*.jpg")]
        print('files',files)
     
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
