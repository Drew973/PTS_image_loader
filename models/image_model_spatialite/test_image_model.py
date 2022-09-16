# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 12:30:57 2022

@author: Drew.Bennett
"""


import unittest
import os

from image_loader.models.setup_database import setupDb
from image_loader.models.image_model_spatialite.image_model import imageModel
from image_loader.models.details.image_details import imageDetails

from PyQt5.QtSql import QSqlDatabase


from image_loader import test


class testImageModel(unittest.TestCase):
    def setUp(self):
        db = QSqlDatabase.addDatabase('QSPATIALITE','image_loader')
        db.setDatabaseName(test.dbFile)
        db.open()
        setupDb(db)
        

    def model(self):
        return imageModel(db = QSqlDatabase.database('image_loader'))


    def csvFile(self):
        return os.path.join(test.testFolder,'outputs','test.csv')

    def generateDbFile(self):
        return os.path.join(test.testFolder,'outputs','test.db')


    def testLoadDetails(self):
        m = self.model()
        c = m.rowCount()

        f = os.path.join(test.testFolder,'inputs','MFV2_01_ImageInt_000005.tif')
        d = imageDetails(f)
        d.findExtents()
        for i in m.addDetails([d]):
            pass
        m.select()
        self.assertEqual(m.rowCount()-c,1)


    def testAddFolder(self):
        m = self.model()
        c = m.rowCount()
        folder = os.path.join(test.testFolder,'inputs','test_folder')
        for i in m.addFolder(folder):
            pass
        m.select()
        self.assertEquals(m.rowCount()-c,191)#191 tif files in folder
    
    
    def testClearTable(self):
        m = self.model()
        m.clearTable()
        self.assertEquals(m.rowCount(),0)
        

    def tearDown(self):
        QSqlDatabase.database('image_loader').close()
        
        #remove csv output
        f = self.csvFile()
        if os.path.exists(f):
            os.remove(f)


    def testSaveAsCsv(self):
        self.model().saveAsCsv(self.csvFile())


    def testSave(self):
        self.assertTrue(self.model().save(self.generateDbFile()))



    
if __name__=='__console__':
    
    layer = m.loadLayer()
    #add virtual field with wkt for debugging.
    field = QgsField('wkt', QVariant.String)
    layer.addExpressionField('geom_to_wkt($geometry)', field)
    
    