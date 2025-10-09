# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 13:41:33 2025

@author: Drew.Bennett
"""
import os
from image_loader import db_functions , file_locations , backend , settings
from PyQt5.QtCore import QProcess



def _intermediateFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '.vrt'


def _warpedFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '_warped.tif'



class georeferenceData:
    
    def __init__(self , inputFile:str , gcps:str , srid:int):
        self.inputFile = inputFile
        self.warpedFile = _warpedFileName(self.inputFile)
        self.gcps = gcps
        self.srid = srid
        
        
    def asQProcess(self , parent = None):
        if os.path.exists(self.inputFile):
            p = QProcess(parent = parent)
            p.setProgram(file_locations.georeference)
            p.setArguments([self.inputFile,_intermediateFileName(self.inputFile),self.warpedFile,self.gcps,'EPSG:'+str(self.srid)])
            #%1:inputFile,%2:intermediate file, %3:outputFile %4:gcp list like '-gcp 0 0 462304.614797396 190867.14791712712 -gcp 1038 1250 462298.4124963682 190865.46511464956' %5 srid
            #args = ['"{a}"'.format(a = arg) for arg in p.arguments()]#double quote in case contain space
           # print(p.program() + ' ' + ' '.join(args))
            return p        
                
        
    
    #-> generator of georeferenceData
def getGeoreferenceData(runPk:int):
    s = backend._getCorrectedSpline(runPk)
    if s is None:
        print('missing GPS?')
    else:
        srid = settings.destSrid()
        qs = 'select frame_id,group_concat(original_file) from images inner join runs on frame_id >= start_frame and frame_id <= end_frame and runs.pk = :pk group by frame_id'
        
        q = db_functions.runQuery(qs,
        values = {':pk':runPk},
        forwardOnly = True)
        #raise db_functions.queryError(q)
        while q.next():
            #raise db_functions.queryError(q)
            frame = q.value(0)
            gcpStr = backend.calcGcps(frame = frame , geom = s)
            for f in q.value(1).split(','):
                yield georeferenceData(inputFile = f , gcps = gcpStr , srid = srid )
           







if __name__ == '__console__':   
    pk = backend.allRunPks()[0]
    print('pk',pk)
    for i,p in enumerate(getGeoreferenceData(pk)):
        if i<5:
            print(p)
            proc = p.asQProcess()
            proc.start()
            proc.waitForFinished()
            
