# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 12:53:40 2025

@author: Drew.Bennett
"""

import os
from PyQt5.QtCore import QProcess

from image_loader import load_image , file_locations , backend
from image_loader.db_functions import runQuery
from qgis.core import QgsProject
from image_loader import georeference
import re
from image_loader import process_runner
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget,QProgressDialog


#data to create/load VRT file
class vrtData:
    
    
    def __init__(self , mfv:str , imageType:str , startFrame : int , endFrame : int , warpedFiles:list[str]):
      #  self.runName = '{tp}_{mfv}_{sf}_to_{ef}'.format(mfv = mfv , sf = startFrame , ef = endFrame , tp = imageType)
        self.mfv = mfv
        self.warpedFiles = warpedFiles
        self.imageType = imageType
        if len(warpedFiles) == 1 :
            folder = os.path.dirname(warpedFiles[0])
        else:
            folder = os.path.commonpath(warpedFiles)
        self.startFrame = startFrame
        self.endFrame = endFrame
        self.vrtFile = os.path.join(folder,self.runName()+'.vrt')
        self.textFile = os.path.join(folder,self.runName()+'.txt')


    def runName(self):
        return '{tp}_{mfv}_{sf}_to_{ef}'.format(mfv = self.mfv , sf = self.startFrame , ef = self.endFrame , tp = self.imageType)
        
        
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
        with open(self.textFile,'w') as tf:
            tf.write('\n'.join(self.warpedFiles))
            
    
    def load(self):
        load_image.loadImage(file = self.vrtFile, groups = ['image_loader','combined VRT',self.imageType,self.mfv])


#remove layers containing warpedFiles.
#uses layer name. more direct way to test what vrt layer contains?
#need this to avoid file lock and invalid layer issues.
    def removeSources(self):        
        for layer in QgsProject.instance().layerTreeRoot().findLayers():
            if self.overlaps(layer.name()):
                QgsProject.instance().removeMapLayers([layer.layerId()])
            
            
    #use layer name to test if layer prevents vrt being overwriten.
    def overlaps(self,name:str):
        pattern = '(\D+)_(.+)_(\d+)_to_(\d+)'
        match = re.match(pattern,name)
        if match:
            tp = match.group(1)
            mfv = match.group(2)
            start = int(match.group(3))
            end = int(match.group(4))
            return tp == self.imageType and mfv == self.mfv and start <= self.endFrame and end >= self.startFrame


                    
                    
  
#data for making vrt from selected runs.
def vrtDataFromRuns(runPks:list[int]) -> list[vrtData]:
    qs = '''select image_type,start_frame,end_frame,group_concat(original_file,'[,]'), runs.mfv_number from runs inner join images on frame_id >= start_frame and frame_id <= end_frame 
    and runs.pk in ({runPks}) and runs.mfv_number = images.mfv_number
    group by image_type,start_frame,end_frame
'''.format(runPks =  ','.join([str(pk) for pk in runPks]))

    query = runQuery(qs)
    d = [] 
    while query.next():        
        originalFiles = query.value(3).split('[,]')
        # existing warped files
        warpedFiles = [os.path.normpath(georeference.warpedFileName(f)) for f in originalFiles]# if os.path.isfile(georeference.warpedFileName(f))
        if warpedFiles:
            d.append(vrtData(imageType = query.value(0) ,
                             mfv = query.value(4),
                             startFrame = query.value(1) ,
                             endFrame = query.value(2) ,
                             warpedFiles = warpedFiles)
                            )
    return d




#connected to action
def makeRunsVrt(data:list[vrtData] , parent:QWidget|None = None):
 

    d = QProgressDialog(parent = parent)
    d.setWindowModality(Qt.WindowModal)
    d.setRange(0,len(data))
    
    d.setLabelText('Removing layers')
    d.show()

    for i,row in enumerate(data):
        row.removeSources()
        if d.wasCanceled():
            return
        d.setValue(i)
        
    
    d.setLabelText('Writing txt files')#io bound. 
    for i,row in enumerate(data):
        if d.wasCanceled():
            return
        row.writeTextFile()
        d.setValue(i)
    
    d.setLabelText('Remaking vrt files')
    processes = [row.asQProcess() for row in data]
    runner = process_runner.beginProcesses(processes = processes , progress = d)
    runner.waitForFinished()

    d.setValue(d.maximum())
    d.hide()
    d.deleteLater()




def test():
    pks = backend.runs_functions.allRunPks()
    d = backend.runs_functions.vrtDataFromRuns([min(pks)])
   # print(d)
    v = d[-1]
    v.writeTextFile()
  
    proc = v.asQProcess()
    proc.waitForFinished()
    print('args:')
    for a in proc.arguments():
        print(a)
    if proc.exitStatus() == QProcess.CrashExit:
        print('error:',proc.readAllStandardError())
    if proc.error() == QProcess.FailedToStart:
        print('not started')
    else:
        print('started')
  #  print(err)
    
    v.load()
    
    
    
def testRemoveSources():
    pks = backend.runs_functions.allRunPks()
    d = backend.runs_functions.vrtDataFromRuns([min(pks)])[-1]
    d.removeSources()
    
    
    
    
if __name__ == '__console__':
    test()
    testRemoveSources()
