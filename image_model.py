# -*- coding: utf-8 -*-
"""
create database and tables in db_functions.createDb().
"""

from PyQt5.QtSql import QSqlQuery,QSqlQueryModel,QSqlDatabase

import os
import csv

from PyQt5.QtCore import Qt
from image_loader.name_functions import generateRun,generateImageId,findOrigonals,generateImageType,projectFolderFromRIL
from image_loader.load_image import loadImage

from image_loader import georeference , layer_functions , db_functions

from image_loader.georeference_commands import georeferenceCommand

from image_loader import run_commands_3 as run_commands
from pathlib import Path
from image_loader.commands_dialog import commandsDialog
from osgeo import gdal
from PyQt5.QtWidgets import QProgressDialog,QApplication

from qgis.utils import iface
from qgis.core import Qgis

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
        


#{vrtFile:(files,type,run)} from primary keys.
#grouped by run,image_type
def vrtData(imagePks : list) -> dict:    
    #use something unlikey to be in file name as seperator.
    p = ','.join([str(pk) for pk in imagePks])
    query = db_functions.runQuery("select group_concat(original_file,'[,]'),run,image_type from images_view where pk in ({pks}) group by run,image_type order by original_file".format(pks = p))
    d = {} # 
    while query.next():
        run = query.value(1)
        tp = query.value(2) 
        # existing warped files
        files = [os.path.normpath(georeference.warpedFileName(f)) for f in query.value(0).split('[,]') if os.path.isfile(georeference.warpedFileName(f))]
       # print(files)
        if files:
            vrtFile = vrtFileName(run = run,imageType = tp, files = files)
            d[vrtFile] = (files,tp,run)
    return d


gdal.UseExceptions()
#vrt_options = gdal.BuildVRTOptions(resampleAlg='cubic', addAlpha=True)
def makeVrtFile(vrtFile,files):
    gdal.SetConfigOption("COMPRESS_OVERVIEW", "LZW")
    gdal.SetConfigOption("INTERLEAVE_OVERVIEW", "PIXEL")   
    gdal.BuildVRT(vrtFile, files)
    ds = gdal.Open(vrtFile, 0)  # 0 = read-only, 1 = read-write. 
    factors = [32,64,128,256,512]
    ds.BuildOverviews("AVERAGE" , factors)
    ds = None


#make vrt files from data like {vrtFile:(files,type,run)...}
def makeLoadVrt(data):
   #print('makeLoadVrt' , data)
    prog = QProgressDialog(labelText = 'remaking VRT files')  
    try:
        vrtFiles = [k for k in data]
        layer_functions.removeSources(vrtFiles)#remove layers to allow file to be edited.
        prog.setMaximum(len(data))
        prog.show()
        for i,vrtFile in enumerate(data):
            QApplication.processEvents()
            if prog.wasCanceled():
                return
            makeVrtFile(vrtFile = vrtFile , files = data[vrtFile][0])
            loadImage(file = vrtFile , groups = ['image_loader', 'combined VRT', data[vrtFile][1], data[vrtFile][2] ] )
            prog.setValue(i)
    except Exception as e:
        iface.messageBar().pushMessage("Image_loader", "Error making VRTs:" + str(e) , level = Qgis.Warning)
    finally:
        prog.close()




def vrtFileName(run , imageType : str , files : []) -> str:
    if len(files) == 1 :
        folder = os.path.dirname(files[0])
    else:
        folder = os.path.commonpath(files)
    return os.path.join(folder,'{tp}_{run}.vrt'.format(run = run,tp = imageType))

    

#return True if images georeferenced. False if user canceled.
def beginGeoreference(gpsModel , pks : list = [] , progress = None , log : str = '') -> bool:
    if pks:
        georeferenceCommands = []
        sources = []#names for georeferenced files
        pkStr = ','.join([str(pk) for pk in pks])
        t = 'select frame_id,group_concat(original_file) from images where pk in ({p}) group by frame_id order by frame_id'.format(p=pkStr)
        q = db_functions.runQuery(t)
        while q.next():
            frame = q.value(0)
            gcp = gpsModel.gcps(frame)
            if gcp is not None:
                #each file in group
                for f in q.value(1).split(','):
                    newFile = georeference.warpedFileName(f)
                    sources.append(newFile)
                    georeferenceCommands.append(georeferenceCommand(inputFile = f , gcps = gcp , srid = gpsModel.srid))
        if log:
            with open(log,'w') as f:
                f.write('\n'.join(georeferenceCommands))
        layer_functions.removeSources(sources)#remove layers to allow file to be edited.
        if georeferenceCommands:
            #print(georeferenceCommands[0])
            prog = commandsDialog(title = 'georeferencing')
            return run_commands.runCommands(commands = georeferenceCommands , progress = prog)







#load images with primary key in pks into qgis
def loadImages(pks:list = []) -> bool: 
    progress = QProgressDialog('Loading images',"Cancel", 0, 1 , parent = None)
    p = ','.join([str(pk) for pk in pks])
    t = 'select original_file,run,image_type from images_view where pk in ({pks}) and not original_file is null'.format(pks = p)
    query = db_functions.runQuery(t)
    progress.setRange(0,query.size())
    progress.show()
    i = 0
    while query.next():
        if progress.wasCanceled():
            return False
        progress.setValue(i)
        warped = georeference.warpedFileName(query.value(0))
        if os.path.exists(warped):
            groups = ['image_loader',
                      query.value(2),
                      query.value(1)]
            loadImage(file=warped,groups=groups)
        i += 1
    progress.close()
    return True
        
    
#only used for testing
def allImagePks():
    pks = []
    query = db_functions.runQuery('select pk from images')
    while query.next():
        pks.append(query.value(0))
    return pks
    
    

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

        

    def addFolder(self,folder):
        files = [str(f) for f in Path(folder).glob("**/*.jpg")]
        self._add([_image(origonalFile = str(f)) for f in files])
    
    
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
