# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 12:30:57 2022

@author: Drew.Bennett
"""

from image_loader.models.image_model_spatialite.setup_database import setupDb
from image_loader.models.image_model_spatialite.image_model import imageModel
from image_loader.models.details.image_details import imageDetails

from PyQt5.QtSql import QSqlDatabase


def test():
    dbFile = r'C:\Users\drew.bennett\Documents\image_loader\test.sqlite'
    db = QSqlDatabase.addDatabase('QSPATIALITE','image_loader')
    db.setDatabaseName(dbFile)
    db.open()
    setupDb(db,overwrite = True)
    assert 'details' in QSqlDatabase.database('image_loader').tables()
    m = imageModel(db = QSqlDatabase.database('image_loader'))
    testClearTable(m)
    testSaveAsCsv(m)
    testLoadDetails(m)
    return m
    
    
def testSaveAsCsv(model):
    model.saveAsCsv(r'C:\Users\drew.bennett\Documents\image_loader\test.csv')
    
    
def testClearTable(m):
    m.clearTable()
    assert m.rowCount()==0
    
    
def testLoadDetails(model):
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\MFV2_01_ImageInt_000005.tif'
    d = imageDetails(f)
    d.findExtents()
    model.addDetails([d])
    
if __name__=='__console__':
    
    m = test()
    QSqlDatabase.database('image_loader').close()
    layer = m.loadLayer()
    #add virtual field with wkt for debugging.
    field = QgsField('wkt', QVariant.String)
    layer.addExpressionField('geom_to_wkt($geometry)', field)
    
    