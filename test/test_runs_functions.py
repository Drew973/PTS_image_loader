# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 10:18:14 2025

@author: Drew.Bennett
"""




import unittest
from image_loader.backend import runs_functions
from qgis.core import QgsProject



class testRunsFunctions(unittest.TestCase):

    def testRunsFromAreas(self):
        areasLayer = QgsProject.instance().mapLayersByName('areas')[0]
        ranges = runs_functions.runsFromAreas(features = areasLayer.getFeatures() , crs = areasLayer.crs() , bearingField = 'bearing')
        print('ranges',ranges)
    
    
    
    
    
if __name__ in ['__main__','__console__']:   
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testRunsFunctions)
    unittest.TextTestRunner().run(suite)