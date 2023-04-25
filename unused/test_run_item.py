# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""





import unittest

from image_loader.run_item import runItem

from image_loader.image import image


class testRunItem(unittest.TestCase):
    def setUp(self):
        self.item = runItem()


    def testAddImages(self):
        images = [image(imageId=1),image(imageId=2)]
        self.item.addImages(images)
        self.assertEqual(self.item.rowCount(),2)


    def testImageFromRow(self):
        images = [image(imageId=1),image(imageId=2)]
        self.item.addImages(images)
        print(self.item.imageFromRow(0))
    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testRunItem)
    unittest.TextTestRunner().run(suite)
  