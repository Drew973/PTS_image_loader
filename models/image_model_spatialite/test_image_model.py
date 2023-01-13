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
        db.setDatabaseName(':memory:')
        if not db.open():
            print(db.lastError().text())
        setupDb(db)
        self.model = imageModel(db = db)


    def testLoadDetails(self):
        c = self.model.rowCount()
        f = os.path.join(test.testFolder,'inputs','MFV2_01_ImageInt_000005.tif')
        d = imageDetails(f)
        d.findExtents()
        self.model.addDetails([d])
        self.assertEqual(self.model.rowCount()-c,1)


    def testAddFolder(self):
        m = self.model
        c = m.rowCount()
        folder = os.path.join(test.testFolder,'inputs','test_folder')
        m.addFolder(folder)
        self.assertEquals(m.rowCount()-c,191)#191 tif files in folder
    
 
    
    def tearDown(self):
        QSqlDatabase.database('image_loader').close()
        #remove csv output



    def testSaveAsCsv(self):
        f = os.path.normpath(os.path.join(test.testFolder,'outputs','test.csv'))
        self.model.saveAsCsv(f)


  #  def testSave(self):
     #   f = os.path.join(test.testFolder,'outputs','test.db')
     #   self.assertTrue(self.model.save(f))


    def testRasterImageLoad(self):
        file = os.path.join(test.testFolder,'inputs','MFV2_01 Raster Image Load File.txt')
        self.model.loadFile(file)
        print(self.model.rowCount())
    
    
if __name__=='__console__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testImageModel)
    unittest.TextTestRunner().run(suite)
   
    #layer = m.loadLayer()
    #add virtual field with wkt for debugging.
    #field = QgsField('wkt', QVariant.String)
  #  layer.addExpressionField('geom_to_wkt($geometry)', field)
    
    