# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader import test
#import cProfile
from image_loader.gps_model_3 import gpsModel
#import cProfile
from qgis.core import QgsPointXY


class testGpsModel(unittest.TestCase):
    
  #  @classmethod
   # def setUpClass(cls):
   #     db_functions.createDb(file = os.path.join(test.testFolder,'test.db'))
    #   # db_functions.createDb()
   

   # @classmethod
   # def tearDownClass(cls):
    #    QSqlDatabase.database('image_loader').close()    
        
    
    def setUp(self):
        self.model = gpsModel()
        self.model.clear()
        file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv')
        self.model.loadFile(file)       


    def testOriginalLine(self):
        line = self.model.originalLine(100,500)
        self.assertTrue(line.isGeosValid())
        
        
    def testLocatePointOriginal(self):
        f = self.model.locatePointOriginal(QgsPointXY(354503.073,322384.628))
        print(f)
        
        
    def testGetFrame(self):
        f = self.model.getFrame(point = QgsPointXY(354503.073,322384.628))
        self.assertEqual(f,455)
        
        
    def testRowCount(self):
        rc = self.model.rowCount()
        self.assertEqual(rc,15374)
        
    def testHasGps(self):
        self.assertTrue(self.model.hasGps())
        
        
   # def tearDown(self):
        #self.model.release()
        
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testGpsModel)
    unittest.TextTestRunner().run(suite)
   
  
  
  