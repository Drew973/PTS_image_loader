# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:14:33 2022

@author: Drew.Bennett
"""
import os
import cProfile, pstats

from image_loader.image_model import image_model
from image_loader import runs_model

from image_loader import exceptions
from PyQt5.QtSql import QSqlDatabase



if __name__ == '__console__':
    from console.console import _console
    testFolder = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)
else:
    testFolder = os.path.dirname(__file__)



def testFromFolder(db):
    folder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01'
    m = image_model.imageModel(db)
    m.fromFolder(folder)
    return m


def profileFromFolder(db):
    with cProfile.Profile() as profiler:
        m = testFromFolder(db)
        
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
    

  
if __name__ == '__main__' or __name__=='__console__':
    from PyQt5.QtWidgets import QTableView
    from qgis.core import QgsProject
    
    dbFile = ":memory:"
        
    db = QSqlDatabase.addDatabase('QSPATIALITE')   #QSqlDatabase
    db.setDatabaseName(dbFile)
    if not db.open():
        raise exceptions.imageLoaderError('could not create database')
        
    image_model.createTable(db)
    
    m = profileFromFolder(db)
    v = QTableView()
    m = testLoadCsv(db)
    testWriteCsv(m)
    m = testLoadTxt(db)
    
    v.setModel(m)
    v.show()
    #m.loadImages()