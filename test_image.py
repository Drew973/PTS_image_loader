# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os

from image_loader import image


from image_loader import test


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from qgis.core import QgsPointXY

import cProfile, pstats


class testImage(unittest.TestCase):
    
    def setUp(self):
        pass

    
    def testLoad(self):
        f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\test_folder\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'
        im = image.image(georeferenced = f)
        
      #  im.load()


    def testRemake(self):
        f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\2023-01-20 15h26m34s LCMS Module 1 000000.jpg'
        to = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\outputs\0000.tif'
        
        im = image.image(file = f)
        im.startPoint = QgsPointXY(430591.318,487612.303)
        im.endPoint = QgsPointXY(430589.548,487616.913)
        
        im.imageType = image.types.intensity#can't tell this from filename.

        im.remake(to = to)

        im.load()
        
    
    
    

        
    def testSort(self):
        images = [image.image(run = 'a',imageId = 10),
                  image.image(run = 'a',imageId = 1),
                  image.image(run = 'b',imageId = 11)]
       
        images2 = sorted(images)
       # print(images2)
        

    def testFromCsv(self):
        f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\cursed.txt'
        images = [i for i in image.fromCsv(f)]
        self.assertEqual(len(images),2108)



if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testImage)
    unittest.TextTestRunner().run(suite)
   
  