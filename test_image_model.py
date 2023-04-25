# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader.image_model import imageModel
from image_loader import test


import cProfile



class testImageModel(unittest.TestCase):
    def setUp(self):
        self.model = imageModel()
        self.model.fields={'folder':os.path.join(test.testFolder,'1_007')}

  #  def testLoadDetails(self):
   #     c = self.model.rowCount()
   #     f = os.path.join(test.testFolder,'inputs','MFV2_01_ImageInt_000005.tif')
   #    # d = imageDetails(f)
  #      d.findExtents()
   #     self.model.addDetails([d])
    #    self.assertEqual(self.model.rowCount()-c,1)


    def testAddFolder(self):
        m = self.model
        c = m.rowCount()
      #  print(c)
        folder = os.path.join(test.testFolder,'inputs','1_007')
        m.addFolder(folder)
        #self.assertEquals(m.rowCount()-c,191)#191 tif files in folder
      #  m.setRun('1_007')
        #self.assertTrue(m.rowCount()>0)
  
    def testSave(self):
        f = os.path.normpath(os.path.join(test.testFolder,'outputs','test.csv'))
        self.model.saveAs(f)


    def testLoadFile(self):
        file = os.path.join(test.testFolder,'inputs','MFV2_01 Raster Image Load File.txt')
        self.model.loadFile(file)
       # self.assertEqual(self.model.rowCount(),400)#should have 400 rows here.
       
        self.model.setRun('MFV2_01')
       # self.assertTrue(self.model.rowCount()>0)
    
       # self.model.mark([self.model.index(0,0)],True)
    
    
    def testRemake(self):
        
        self.model.addFolder(os.path.join(test.testFolder,'1_007'))
        gps = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv')
        self.model.loadGps(gps)
        
        
        indexes = [self.model.index(i,0) for i in range(10)]
        self.model.remakeImages(indexes)
        
        
        
    
    
    
    def tearDown(self):
        self.model.database().close()
    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testImageModel)
    unittest.TextTestRunner().run(suite)
   
    #layer = m.loadLayer()
    #add virtual field with wkt for debugging.
    #field = QgsField('wkt', QVariant.String)
  #  layer.addExpressionField('geom_to_wkt($geometry)', field)