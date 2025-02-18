# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 12:53:40 2025

@author: Drew.Bennett
"""

import os
from PyQt5.QtCore import QProcess

from image_loader import load_image , file_locations , backend

from qgis.core import QgsProject

import re


#data to create/load VRT file
class vrtData:
    
    
    def __init__(self , imageType , startFrame : int , endFrame : int , warpedFiles):
        self.runName = '{tp}_{sf}_to_{ef}'.format(sf = startFrame , ef = endFrame , tp = imageType)
        self.warpedFiles = warpedFiles
        self.imageType = imageType
        if len(warpedFiles) == 1 :
            folder = os.path.dirname(warpedFiles[0])
        else:
            folder = os.path.commonpath(warpedFiles)
        self.vrtFile = os.path.join(folder,self.runName+'.vrt')
        self.textFile = os.path.join(folder,self.runName+'.txt')
        self.startFrame = startFrame
        self.endFrame = endFrame


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
        load_image.loadImage(file = self.vrtFile, groups = ['image_loader','combined VRT',self.imageType])


#remove layers containing warpedFiles.
#uses layer name. more direct way to test what vrt layer contains?
#need this to avoid file lock and invalid layer issues.
    def removeSources(self):        
        for layer in QgsProject.instance().layerTreeRoot().findLayers():
            #print(layer.name())
            #{type}_{startFrame}_to_{endFrame}.vrt
            pattern = '(\D+)_(\d+)_to_(\d+)'
            match = re.match(pattern,layer.name())
            if match:
                tp = match.group(1)
                start = int(match.group(2))
                end = int(match.group(3))
                print(tp,start,end)
        
                if tp == self.imageType and start <= self.endFrame and end >= self.startFrame:
                    print('removing:'+layer.name())
                    QgsProject.instance().removeMapLayers([layer.layerId()])
                        



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
