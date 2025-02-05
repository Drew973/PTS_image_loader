# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 13:41:33 2025

@author: Drew.Bennett
"""
import os
from image_loader import db_functions , gps_model , file_locations
from PyQt5.QtCore import QProcess



#only used for testing
def allImagePks():
    pks = []
    query = db_functions.runQuery('select pk from images')
    while query.next():
        pks.append(query.value(0))
    return pks
    

#'[(x,y,pixel,line)]'
def georeferenceProcess(inputFile , outputFile , gcp , srid):
    p = QProcess()
    p.setProgram(file_locations.georeference)
    p.setArguments([inputFile,intermediateFileName(inputFile),outputFile,gcp,'EPSG:'+str(srid)])   
    #%1:inputFile,%2:intermediate file, %3:outputFile %4:gcp list like '-gcp 0 0 462304.614797396 190867.14791712712 -gcp 1038 1250 462298.4124963682 190865.46511464956' %5 srid
    return p



#->generator of QProcess
def georeferenceProcesses(gpsModel , imagePks : list):
    pkStr = ','.join([str(pk) for pk in imagePks])
    t = 'select frame_id,group_concat(original_file) from images where pk in ({p}) group by frame_id order by frame_id'.format(p=pkStr)
    q = db_functions.runQuery(t)
    processes = []
    layerSources = []
    errors = []
    while q.next():
        frame = q.value(0)
        gcp = gpsModel.gcps(frame)
       # print(gcp)
        for f in q.value(1).split(','):
            if os.path.exists(f):
                newFile = warpedFileName(f)
                processes.append(georeferenceProcess(f,newFile,gcp,gpsModel.srid))
                layerSources.append(newFile)
            else:
                errors.append('no file named "{f}"'.format(f=f))     
                
    return (processes,layerSources,errors)
      


def warpedFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '_warped.tif'


def intermediateFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '.vrt'

if __name__ == '__console__':
    g = gps_model.gpsModel()
    pks = allImagePks()[0:5]
    for p in georeferenceProcesses(g,pks):
        print(p)
