# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:14:33 2022

@author: Drew.Bennett
"""
import os
import cProfile, pstats

from image_loader.models.image_model import image_model
#from image_loader.models import runs_model

from image_loader import exceptions
from image_loader.test.get_db import getDb



if __name__ == '__console__':
    from console.console import _console
    testFolder = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)
else:
    testFolder = os.path.dirname(__file__)



def testFromFolder(m):
    folder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01'
    m.fromFolder(folder)


def profileFromFolder(m):
    with cProfile.Profile() as profiler:
        testFromFolder(m)
        
    f = os.path.join(testFolder,'convert_folder_profile.txt')
   
    profiler.dump_stats(f)
        
    with open(f, 'w') as to:
        stats = pstats.Stats(profiler, stream=to)
        stats.sort_stats('cumtime')
        stats.print_stats()
    return m
    
def testWriteCsv(m):
    f = os.path.join(testFolder,r'outputs\test_write.csv')
    m.saveAsCsv(f)
    return m


  
def testLoadCsv(db):
    f = os.path.join(testFolder,r'inputs/test.csv')
    m = image_model.imageModel(db)
    m.loadCsv(f)
    return m
  
    
def testLoadTxt(db):  
    f = os.path.join(testFolder,r'inputs/TXY_Y Raster Image Load File.txt')
    m = image_model.imageModel(db)
    m.loadCsv(f)
    return m
    

def testInit(db=getDb()):
    image_model.createTable(db)
    return image_model.imageModel(db)

  
def testDetailsFromSelectedFeatures(m):
    layer = QgsProject.instance().mapLayersByName('MFV2_15 Spatial Frame Data')[0]
    print(m.detailsFromSelectedFeatures(layer,'fileName','fileName'))
    
  
if __name__ == '__main__' or __name__=='__console__':
    from PyQt5.QtWidgets import QTableView
    from qgis.core import QgsProject
    
    m = testInit()
    profileFromFolder(m)
    v = QTableView()
   # m = testLoadCsv(db)
    #testWriteCsv(m)
   # m = testLoadTxt(db)
   
    testDetailsFromSelectedFeatures(m)
    
    v.setModel(m)
    v.show()
    #m.loadImages()