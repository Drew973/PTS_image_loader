# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 12:53:40 2025

@author: Drew.Bennett
"""

import os
from PyQt5.QtCore import QProcess

from image_loader import georeference , db_functions , load_image , file_locations
from image_loader.image_model import allImagePks



#data to create/load VRT file
class vrtData:
    
    
    def __init__(self , imageType , run , warpedFiles):
        self.imageType = imageType
        self.run = run
        self.vrtFile = vrtFileName(run = run , imageType = imageType , files = warpedFiles)
        self.root = os.path.commonpath(warpedFiles)
        #self.warpedFiles = [os.path.relpath(f,self.root) for f in warpedFiles]
        self.warpedFiles = warpedFiles
        self.textFile = ''
        

    #windows CLI has 8191 charactor limit. does it apply to QProcess?
    def asQProcess(self) -> QProcess:
        p = QProcess()
       # interpreter = r'C:\Program Files\QGIS 3.18\apps\Python37\python.exe'
        p.setProgram(file_locations.makeVrt)#bat or exe
        p.setArguments([str(self.vrtFile) , self.textFile])
        return p
        
    
    #write text file containing list of filenames.
    #need this because limit on CLI charactors.
    def writeTextFile(self):
        self.textFile = os.path.splitext(self.vrtFile)[0] + '.txt'
        with open(self.textFile,'w') as tf:
            tf.write('\n'.join(self.warpedFiles))
            
    
    def load(self):
        load_image.loadImage(file = self.vrtFile, groups = ['image_loader','combined VRT',self.imageType,self.run])



def vrtFileName(run , imageType : str , files : []) -> str:
    if len(files) == 1 :
        folder = os.path.dirname(files[0])
    else:
        folder = os.path.commonpath(files)
    return os.path.join(folder,'{tp}_{run}.vrt'.format(run = run,tp = imageType))
        

    
#{vrtFile:(files,type,run)} from primary keys.
#grouped by run,image_type
def getVrtData(imagePks : list) -> list:    
    #use something unlikey to be in file name as seperator.
    p = ','.join([str(pk) for pk in imagePks])
    query = db_functions.runQuery("select group_concat(original_file,'[,]'),run,image_type from images_view where pk in ({pks}) group by run,image_type order by original_file".format(pks = p))
    d = [] # 
    while query.next():
        run = query.value(1)
        tp = query.value(2) 
        # existing warped files
        files = [os.path.normpath(georeference.warpedFileName(f)) for f in query.value(0).split('[,]') if os.path.isfile(georeference.warpedFileName(f))]
       # print(files)
        if files:
            #vrtFile = vrtFileName(run = run,imageType = tp, files = files)
            #d[vrtFile] = (files,tp,run)
            d.append(vrtData(imageType = tp , run = run , warpedFiles = files))
    return d


    #'/d+_warped.tif'



def test():
    pks = allImagePks()
    #print(pks)
    d = getVrtData(pks)
   # print(d)
    v = d[-1]
   # print(v.vrtFile)
  #  print(v.warpedFiles)
    
    #print(v.warpedFiles)
    
    v.writeTextFile()
  
    proc = v.asQProcess()
    proc.waitForFinished()
    
  #  print(json.dumps(v.warpedFiles))
  
    print('args:')
    for a in proc.arguments():
        print(a)
    
    if proc.exitStatus() == QProcess.CrashExit:
        print('error:',proc.readAllStandardError())

    
  #  QProcess.ProcessError
    if proc.error() == QProcess.FailedToStart:
        print('not started')
    else:
        print('started')
  #  print(err)
    
    v.load()
    
 #   print(proc.arguments())
    
    #fl = ['{f}'.format(f=f) for f in v.warpedFiles[0:5]]
    #print(';'.join(fl))
if __name__ == '__console__':
    test()
    
