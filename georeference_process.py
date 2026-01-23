# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 13:41:33 2025

@author: Drew.Bennett
"""
import os
from image_loader import db_functions , gps_model , file_locations , settings
from PyQt5.QtCore import QProcess



#only used for testing
def allImagePks():
    pks = []
    query = db_functions.runQuery('select pk from images')
    while query.next():
        pks.append(query.value(0))
    return pks
    

#'[(x,y,pixel,line)]'
def georeferenceProcess(inputFile:str , outputFile:str , gcp:str , srid:int):
    p = QProcess()
    p.setProgram(file_locations.georeference)
    p.setArguments([inputFile,intermediateFileName(inputFile),outputFile,gcp,'EPSG:'+str(srid)])   
    #%1:inputFile,%2:intermediate file, %3:outputFile %4:gcp list like '-gcp 0 0 462304.614797396 190867.14791712712 -gcp 1038 1250 462298.4124963682 190865.46511464956' %5 srid
    return p



def georeferenceProcesses(imagePks : list[int]):
    pkStr = ','.join([str(pk) for pk in imagePks])
    
    qs = '''
select original_file
,group_concat('-gcp '||pixel||' '||line||' '||x||' '||y,' ')
from images inner join gcp on images.frame_id = gcp.frame and images.mfv_number = gcp.mfv_number and pk in ({p})
group by original_file    
    '''.format(p=pkStr)
    
    
  #  t = 'select frame_id,group_concat(original_file) from images where pk in ({p}) group by frame_id order by frame_id'.format(p=pkStr)
    q = db_functions.runQuery(qs)
    processes = []
    layerSources = []
    errors = []
    while q.next():
        originalFile = q.value(0)
        gcp = q.value(1)#like -gcp 0 0 462304.614797396 190867.14791712712 -gcp 1038 1250 462298.4124963682 190865.46511464956
        #pixel line x y
        #print(gcp)
        if os.path.exists(originalFile):
            newFile = warpedFileName(originalFile)
            processes.append(georeferenceProcess(inputFile = originalFile , outputFile = newFile , gcp = gcp , srid = settings.destSrid()))
            layerSources.append(newFile)
        else:
            errors.append('no file named "{f}"'.format(f=originalFile))     
                
    return (processes,layerSources,errors)
      


def warpedFileName(origonalFile:str):
    return os.path.splitext(origonalFile)[0] + '_warped.tif'


def intermediateFileName(origonalFile:str):
    return os.path.splitext(origonalFile)[0] + '.vrt'

if __name__ == '__console__':
    g = gps_model.gpsModel()
    pks = allImagePks()[0:5]
    for p in georeferenceProcesses(g,pks):
        print(p)
