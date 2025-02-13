# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader import test,download_distress
#import cProfile
from image_loader.gps_model import gpsModel

import cProfile
import os

class testDownloadDistresses(unittest.TestCase):
    
#    @classmethod
#    def setUpClass(cls):
   #     db_functions.createDb(file = os.path.join(test.testFolder,'test.db'))
    #   # db_functions.createDb()
   

   # @classmethod
   # def tearDownClass(cls):
    #    QSqlDatabase.database('image_loader').close()    
        
    
    def setUp(self):
        self.model = gpsModel()
      

    def testDownloadFaulting(self):
        profileFile = os.path.join(test.profileFolder,'downloadFaulting.prof')
        pr = cProfile.Profile()
        pr.enable()
        layer = download_distress.downloadFaulting(gpsModel = self.model)
        pr.disable()
        pr.dump_stats(profileFile)#
        self.assertGreater(layer.featureCount(), 0 , 'no features in layer')


    def testLoadLayer(self):
        self.model.downloadGpsLayer()
    
    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testDownloadDistresses)
    unittest.TextTestRunner().run(suite)
