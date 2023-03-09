# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""





import unittest
import os

from image_loader.details_tree_model import detailsTreeModel


from image_loader import test


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog


import cProfile, pstats



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
    
    
    #profile how long loading images into QGIS takes
    def testProfileLoad(self):
        file = os.path.join(test.testFolder,'inputs','test2.csv')
        profile = os.path.join(test.testFolder,'loadImages.prof')
        profile2 = os.path.join(test.testFolder,'loadImages2.prof')

        
        self.model.loadFile(file,load=True)


        pr = cProfile.Profile()
        pr.enable()        
        progress = QProgressDialog("Loading images...","Cancel", 0, 0)
       # progress.setMinimumDuration(0)
        progress.setWindowModality(Qt.WindowModal)
        self.model.loadImages(progress = progress)
        progress.setValue(progress.maximum())#double check progress reaches 100%
        progress.deleteLater()
        
        pr.disable()
        
        
        pr.dump_stats(profile)#compatible with snakeviz
        
        with open(profile2, 'w') as to:
            stats = pstats.Stats(pr, stream=to)
            stats.sort_stats('cumtime')
            stats.print_stats()
    
    
    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testDetailsModel)
    unittest.TextTestRunner().run(suite)
   
    #layer = m.loadLayer()
    #add virtual field with wkt for debugging.
    #field = QgsField('wkt', QVariant.String)
  #  layer.addExpressionField('geom_to_wkt($geometry)', field)