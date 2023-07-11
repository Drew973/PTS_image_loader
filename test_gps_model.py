# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader import test
#import cProfile
from image_loader.gps_model_sqlite import gpsModel
#import cProfile



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

    def testLoadCsv(self):
        file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv')
        self.model.loadCsv(file)       

    
    
    def tearDown(self):
        self.model.release()
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testGpsModel)
    unittest.TextTestRunner().run(suite)
   
  
  
  