# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 15:30:28 2023

@author: Drew.Bennett
"""

import unittest
from image_loader import runs_model,db_functions
from image_loader import test
import os
from qgis.core import QgsProject

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
        
    
    def testInsert(self):
        data = [{'start_frame': 1, 'end_frame': 200}, {'start_frame': 1486, 'end_frame': 1827}, {'start_frame': 3112, 'end_frame': 3455}, {'start_frame': 4739, 'end_frame': 5083}, {'start_frame': 6363, 'end_frame': 6694}, {'start_frame': 7980, 'end_frame': 8202}, {'start_frame': 8214, 'end_frame': 8215}, {'start_frame': 679, 'end_frame': 1008}, {'start_frame': 2306, 'end_frame': 2634}, {'start_frame': 3933, 'end_frame': 4261}, {'start_frame': 5561, 'end_frame': 5885}]
        runs_model.insertRuns(data)
    
    
    
    def testRunsFromAreas(self):
        areasLayer = QgsProject.instance().mapLayersByName('areas')[0]
        ranges = runs_model.runsFromAreas(features = areasLayer.getFeatures() , crs = areasLayer.crs())
        print('ranges',ranges)
        
        
if __name__ in ['__main__','__console__']:   
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testRunsModel)
    unittest.TextTestRunner().run(suite)