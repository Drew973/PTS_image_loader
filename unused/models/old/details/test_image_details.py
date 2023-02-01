# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:48:26 2022

@author: Drew.Bennett
"""


import os
import unittest
from image_loader.models.details import image_details
from image_loader import test


class testDetails(unittest.TestCase):

    def setUp(self):
        self.file = os.path.join(test.testFolder,'inputs','MFV2_01_ImageInt_000005.tif')




    def testValues(self):
        d = image_details.imageDetails(self.file)
        d.findExtents()
        self.assertEqual(d['run'],'MFV2_01')
        self.assertEqual(d['imageId'],5)



    def testLoad(self):
        d = image_details.imageDetails(self.file)
        d.load()    
        
        
    