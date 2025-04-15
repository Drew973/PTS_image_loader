# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader.backend import gps_functions
from image_loader import db_functions , test
from image_loader.test import testFolder




def testrecalcSpline():
    gps_functions.recalcSpline()
    


class testGpsFunctions(unittest.TestCase):
    
    
    @classmethod
    def setUpClass(cls):
        db_functions.setFile(test.dbFile)

    
    def setUp(self):
        pass
    
    
    def testUploadAnpp(self):
        inFile = r'C:\Users\drew.bennett\Documents\athens_airport\data\2024-10-17\20241017_03\2024-10-17 01h41m32s Gipsi2 Module 1 20241017_03 001.anpp'
        gps_functions.uploadAnpp(inFile)
        #s = gps_functions.getSplineString()
        
        
        
    def testUploadCsv(self):
        f = r'E:\Manchester_Airport\Hawkeye Exported Data\20250219_08-rutacd-1.csv'
        test.profileFunction(gps_functions.uploadCsv,{'filePath' : f})



#CSV that isn't rutacd
    def estUploadGeomCsv(self):
        inFile = os.path.join(testFolder,'20241018_07-geom-1.csv')
        gps_functions.uploadCsv(inFile)
       # s = gps_functions.getSplineString()


    def estGetSplineString(self):
        s = gps_functions.getSplineString()
        
    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testGpsFunctions)
    unittest.TextTestRunner().run(suite)
    #testrecalcSpline()
