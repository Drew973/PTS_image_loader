# -*- coding: utf-8 -*-
"""
Created on Fri May 19 07:34:38 2023

@author: Drew.Bennett
"""


import csv
import os
import glob
import re
from PyQt5.QtCore import Qt


from PyQt5.QtWidgets import QProgressDialog

from image_loader.run_commands import runCommands


#digits at end of filename without extention
# str -> int
def generateImageId(filePath):
    name = os.path.splitext(os.path.basename(filePath))[0]
    m = re.search('\d+$', name)
    if m:
        return int(m.group(0))
    else:
        return -1

    
template = 'gdalwarp -s_srs EPSG:27700 -t_srs EPSG:27700 -b 1 -colorinterp_1 gray -of COG -co COMPRESS=JPEG -co OVERVIEWS=IGNORE_EXISTING -co QUALITY=70 "{source}" "{dest}" -a_nodata -1'

#warp every jpg in both corrections file and inputFolder

def prepareFolder(inputFolder,outputFolder,corrections):    
    
    progress = QProgressDialog("finding files...","Cancel", 0, 1)
    progress.setAutoClose(False)
    progress.setWindowModality(Qt.WindowModal)
    progress.show()
    progress.forceShow()
    
    images = {}
    pattern = inputFolder+'\*.jpg'
    for f in glob.glob(pattern):    
        images[generateImageId(f)] = f
        
        
    #print(images)
    vrtCommands = []    
    with open(corrections,'r') as f:
        reader = csv.DictReader (f)
        for d in reader:
            if progress.wasCanceled():
                return
            run = d['RunID']
            vrt = os.path.join(outputFolder,run+'.vrt')
            textFile = os.path.join(outputFolder,run+'.txt')
            #print(d,run,vrt)
            
            inputFiles = [images[image_id] for image_id in range(int(d['FromFrame']),int(d['ToFrame'])+1) if image_id in images]
            outputFiles = [os.path.join(outputFolder,os.path.splitext(os.path.basename(f))[0]+'.tif') for f in inputFiles]
            warpCommands = [template.format(source = inputFile,dest = outputFiles[i]) for i,inputFile in enumerate(inputFiles) if not os.path.exists(outputFiles[i])]
                
            progress.setLabelText('warping '+run)
            print(warpCommands[0])
            #runCommands(warpCommands,progress)
            
            progress.setLabelText('Writing txt for '+run)
            with open(textFile,'w') as tf:
               tf.write('\n'.join(outputFiles))
               
            vrtCommands.append ('gdalbuildvrt "{vrt}" -input_file_list "{textFile}" -a_srs "EPSG:27700"'.format(vrt=vrt,textFile = textFile))
    
    progress.setLabelText('making vrts')
    #runCommands(vrtCommands,progress) 
    print(vrtCommands)
   # print(vrtCommands)   
    progress.close()#close immediatly otherwise haunted by ghostly progressbar
    progress.deleteLater()
    del progress
    

inputFolder = r'D:\RAF Shawbury\Data\2023-01-21\MFV1_006\Run 8\LCMS Module 1\Images\RangeWithoutOverlay'
outputFolder = r'D:\RAF Shawbury\TIF Images\MFV1_006\range'
corrections = r'D:\RAF Shawbury\Processed Data\MFV1_006 Coordinate Corrections.csv'    
    
prepareFolder(inputFolder,outputFolder,corrections) 
    