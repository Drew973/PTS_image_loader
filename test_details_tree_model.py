# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""





import unittest
import os

from image_loader.details_tree_model import detailsTreeModel


from image_loader import test


class testDetailsModel(unittest.TestCase):
    def setUp(self):
        self.model = detailsTreeModel()


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
        print(c)
        folder = os.path.join(test.testFolder,'inputs','test_folder')
        m.addFolder(folder)
        #self.assertEquals(m.rowCount()-c,191)#191 tif files in folder
    
 
  
    def testSaveAsCsv(self):
        f = os.path.normpath(os.path.join(test.testFolder,'outputs','test.csv'))
        self.model.save(f)


  #  def testSave(self):
     #   f = os.path.join(test.testFolder,'outputs','test.db')
     #   self.assertTrue(self.model.save(f))


    def testRasterImageLoad(self):
        file = os.path.join(test.testFolder,'inputs','MFV2_01 Raster Image Load File.txt')
        self.model.loadFile(file)
       # self.assertEqual(self.model.rowCount(),400)#should have 400 rows here.
    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testDetailsModel)
    unittest.TextTestRunner().run(suite)
   
    #layer = m.loadLayer()
    #add virtual field with wkt for debugging.
    #field = QgsField('wkt', QVariant.String)
  #  layer.addExpressionField('geom_to_wkt($geometry)', field)