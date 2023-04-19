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
from qgis.core import QgsPointXY,QgsProject

import cProfile, pstats


class testImage(unittest.TestCase):



    def testRemake(self):
        f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\2023-01-20 15h26m34s LCMS Module 1 000000.jpg'
        to = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\outputs\0000.tif'
        
        im = image.image(file = f)
        im.startPoint = QgsPointXY(430591.318,487612.303)
        im.endPoint = QgsPointXY(430589.548,487616.913)
        
        im.imageType = image.types.intensity#can't tell this from filename.

        im.remake(to = to)

        im.load()
    
    def setUp(self):
        pass

    
    def testLoad(self):
        f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\test_folder\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'
        im = image.image(georeferenced = f)
        
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


    

class testImages(unittest.TestCase):
    
    def setUp(self):
        folder = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs'
        files = [f for f in os.listdir(folder) if os.path.splitext(f)[-1] == '.jpg']
        outputFolder = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\outputs'
        self.images = []
        
        for f in files:
            file = os.path.join(folder,f)
            georeferenced = os.path.normpath(os.path.join(outputFolder,os.path.splitext(os.path.basename(file))[0]+'.tif'))
            im = image.image(file = file,georeferenced = georeferenced)
       #     im.startPoint = QgsPointXY(355203.126,321922.095)
          #  im.endPoint = QgsPointXY(355209.064,321919.791)
            im.imageType = image.types.intensity
            im.startM = im.imageId * 5
            im.endM = im.startM + 5
            self.images.append(im)
      

    
    def testRemake(self):
        #print(self.images[0].temp)
        #QProgressDialog()
        image.remakeImages(self.images,progress = QProgressDialog())

        for i in self.images:
            i.load()


    def testRecalc(self):
        gps = QgsProject.instance().mapLayersByName('gps')
        assert len(gps)>0
        gps = gps[0]
        sField = 'startM'
        eField = 'endM'

        image.remakeImages(images = self.images,progress = QProgressDialog(),layer = gps,startField=sField,endField = eField)

        for i in self.images:
            i.load()


if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testImage)
    unittest.TextTestRunner().run(suite)
   
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testImages)
    unittest.TextTestRunner().run(suite)