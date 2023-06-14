# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 15:30:28 2023

@author: Drew.Bennett
"""

import unittest
from image_loader import corrections_model,db_functions
from image_loader import test
import os
from PyQt5.QtSql import QSqlDatabase
from qgis.core import QgsPointXY


class testCorrectionModel(unittest.TestCase):
    
    
    def setUp(self):
        db_functions.createDb(file = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\test.db')
        self.model = corrections_model.correctionsModel()

        
    def testGetChainage(self):
        db_functions.loadGps(file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv'),db = self.model.database())
        index = self.model.index(0,0)
        p = QgsPointXY(354445.563,321924.132)
        ch = self.model.getChainage(index = index,point = p)#offset wrong.should be ~14.4
        print('getChainage',ch)
        if ch:
            p2 = self.model.getPoint(chainage = ch[0], offset = ch[1], index = None)
            print(p2)
            d = p2.distance(p)
            print('d',d)
            self.assertTrue(d<0.001)#within 1cm



    def testLoadCorrection(self):   
        corrections = os.path.join(test.testFolder,'1_007','MFV1_007 Coordinate Corrections.csv')
        self.model.clear()
        self.model.loadFile(corrections)
    
    
    def tearDown(self):
        self.model.database().close()
    
    
    @classmethod
    def setUpClass(cls):
        pass
        
        
if __name__ in ['__main__','__console__']:   
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testCorrectionModel)
    unittest.TextTestRunner().run(suite)