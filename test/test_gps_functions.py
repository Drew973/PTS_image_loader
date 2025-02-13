# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader import test
from image_loader.backend import gps_functions




class testGpsFunctions(unittest.TestCase):
    

    
    def setUp(self):
        pass
    
    
    def testUploadAnpp(self):
        inFile = r'C:\Users\drew.bennett\Documents\athens_airport\data\2024-10-17\20241017_03\2024-10-17 01h41m32s Gipsi2 Module 1 20241017_03 001.anpp'
        gps_functions.uploadAnpp(inFile)
        s= gps_functions.getSplineString()


    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testGpsFunctions)
    unittest.TextTestRunner().run(suite)
