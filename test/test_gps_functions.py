# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader.backend import gps_functions


import numpy as np
from image_loader.test import profileFolder,testFolder
import cProfile



def testGetSplineString():
    profileFile = os.path.join(profileFolder,'getSplineString.prof')
    pr = cProfile.Profile()
    pr.enable()
    s = gps_functions.getSplineString(srid = 27700)
    pr.disable()
    pr.dump_stats(profileFile)
    




def testrecalcSpline():
    gps_functions.recalcSpline()
    


class testGpsFunctions(unittest.TestCase):
    

    
    def setUp(self):
        pass
    
    
    def testUploadAnpp(self):
        inFile = r'C:\Users\drew.bennett\Documents\athens_airport\data\2024-10-17\20241017_03\2024-10-17 01h41m32s Gipsi2 Module 1 20241017_03 001.anpp'
        gps_functions.uploadAnpp(inFile)
        s= gps_functions.getSplineString()



#CSV that isn't rutacd
    def testUploadGeomCsv(self):
        inFile = os.path.join(testFolder,'20241018_07-geom-1.csv')
        gps_functions.uploadCsv(inFile)
        s= gps_functions.getSplineString()


    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testGpsFunctions)
    unittest.TextTestRunner().run(suite)
    #testrecalcSpline()
