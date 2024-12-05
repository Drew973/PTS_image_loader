# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 15:30:28 2023

@author: Drew.Bennett
"""

import unittest
from image_loader import runs_model,db_functions
from image_loader import test
import os


db_functions.createDb()


class testRunsModel(unittest.TestCase):
    
    def setUp(self):
        self.model = runs_model.runsModel()


    def testLoadSaveCollatorCsv(self):
        corrections = os.path.join(test.testFolder,'MFV1_001_Coordinate_Corrections_collator_style.csv')
        self.model.clear()
        self.model.loadCsv(corrections)
        self.assertEqual(self.model.rowCount(),7,'rowCount should be 7 after loading MFV1_001_Coordinate_Corrections_collator_style.csv')
    
    
        to = os.path.join(test.testFolder,'MFV1_001_Coordinate_Corrections_collator_style_output.csv')
        self.model.saveCsv(to)
    
    
    def testLoadOldCsv(self):
        corrections = os.path.join(test.testFolder,'1_007','MFV1_007 Coordinate Corrections_old_style.csv')
        self.model.clear()
        self.model.loadCsv(corrections)
        self.assertEqual(self.model.rowCount(),85,'rowCount should be 85 after loading MFV1_007 Coordinate Corrections_old_style.csv')
    
    
    def tearDown(self):
        self.model.database().close()
    
    
    @classmethod
    def setUpClass(cls):
        pass
        
        
if __name__ in ['__main__','__console__']:   
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testRunsModel)
    unittest.TextTestRunner().run(suite)