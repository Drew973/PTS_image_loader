# -*- coding: utf-8 -*-
"""
Created on Thu May 25 08:52:40 2023

@author: Drew.Bennett
"""


from image_loader import name_functions,run_commands

import glob
import os


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog


def makeHybrids(intensityFolder,rangeFolder,hybridFolder,mfv='1_005'):
    
    progress = QProgressDialog("translating files...","Cancel", 0, 1)
    progress.setAutoClose(False)
    progress.setWindowModality(Qt.WindowModal)
    progress.setLabelText('finding files')
    progress.show()
    progress.forceShow()
    
    
    data = {} # id,intensity,range
    
    for f in glob.glob(intensityFolder+'\*.tif'):
        data[name_functions.generateImageId(f)] = [f,None]

    for f in glob.glob(rangeFolder+'\*.tif'):
        data[name_functions.generateImageId(f)] [1] = f


    print(data)
    
    
    template = 'gdalbuildvrt -b 1 -overwrite -a_srs EPSG:27700 -srcnodata "0 0 0 0" -vrtnodata 0 -separate -input_file_list "{fileList}" "{dest}"'
    
    
    mergeCommands = []
    progress.setMaximum(len(data))
    progress.setLabelText('writing text files')

    
    for i,d in enumerate(data):
        progress.setValue(i)
        
        if progress.wasCanceled():
            return
        
       # name = os.path.join(hybridFolder,'MFV{mfv}_hybrid_{imageId:05d}'.format(mfv=mfv,imageId = d))# like MFV1_006_hybrid_00000
        name = os.path.join(hybridFolder,'MFV{mfv}_hybrid_{imageId}'.format(mfv=mfv,imageId = d))

        fileList = name+'.txt'
        if i<999999999:
            #print(fileList)
            with open(fileList,'w') as fl:
                fl.write('{intensity}\n{rg}'.format(intensity=data[d][0],rg = data[d][1]))
        
            mergeCommands.append(template.format(fileList=fileList,dest=name+'.vrt'))
    
    #print(mergeCommands)
    progress.setLabelText('writing vrt files')
    run_commands.runCommands(commands=mergeCommands,progress=progress)
    
    

if __name__ in ('__main__','__console__'):

    intensityFolder = r'D:\RAF Shawbury\TIF Images\MFV1_005\ImageInt'
    rangeFolder = r'D:\RAF Shawbury\TIF Images\MFV1_005\ImageRng'
    
    hybridFolder = r'D:\RAF Shawbury\TIF Images\MFV1_005\hybrid'
    
    makeHybrids(intensityFolder,rangeFolder,hybridFolder)


