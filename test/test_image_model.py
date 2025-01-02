# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os


import cProfile
from image_loader import runs_model,db_functions,gps_model,test,image_model
from PyQt5.QtSql import QSqlDatabase
db_functions.createDb()

folder1007 = os.path.join(test.testFolder,'1_007')


class testImageModel(unittest.TestCase):
    

    @classmethod
    def tearDownClass(cls):
        QSqlDatabase.database('image_loader').close()    
    
        
    def setUp(self):
        self.model = image_model.imageModel()
        self.gpsModel = gps_model.gpsModel()
        

  #  def testLoadDetails(self):
   #     c = self.model.rowCount()
   #     f = os.path.join(test.testFolder,'inputs','MFV2_01_ImageInt_000005.tif')
   #    # d = imageDetails(f)
  #      d.findExtents()
   #     self.model.addDetails([d])
    #    self.assertEqual(self.model.rowCount()-c,1)


    def estAddFolder(self):
        m = self.model
        c = m.rowCount()
      #  print(c)
        m.addFolder(folder1007)
        #self.assertEquals(m.rowCount()-c,191)#191 tif files in folder
      #  m.setRun('1_007')
        #self.assertTrue(m.rowCount()>0)
  
    def estSave(self):
        f = os.path.normpath(os.path.join(test.testFolder,'outputs','test.csv'))
        self.model.saveAs(f)


    def estLoadFile(self):
        file = os.path.join(test.testFolder,'inputs','MFV2_01 Raster Image Load File.txt')
        self.model.loadRIL(file)
       # self.assertEqual(self.model.rowCount(),400)#should have 400 rows here.
       
        self.model.setRun('MFV2_01')
       # self.assertTrue(self.model.rowCount()>0)
    
       # self.model.mark([self.model.index(0,0)],True)
    
    
    def testGeoreference(self):
        #use images on external hdd for better indicator of performance.
        self.model.clear()
        gps = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv')
        self.gpsModel.loadFile(gps)
        self.model.addFolder(os.path.join(test.testFolder,'1_007'))
        
        corrections = os.path.join(test.testFolder,'1_007','MFV1_007 Coordinate Corrections.csv')
        correctionsModel = runs_model.runsTableModel()
        correctionsModel.clear()
        correctionsModel.loadCsv(corrections)
        keys = self.model.allImagePks()
     #   print('keys',keys)
        
        profileFile = os.path.join(test.profileFolder,'georeference.prof')
        print('snakeviz "{f}"'.format(f = profileFile))
        
        pr = cProfile.Profile()
        pr.enable()
        self.model.georeference(self.gpsModel , keys)
        pr.disable()
        pr.dump_stats(profileFile)
    
    
    def tearDown(self):
        self.model.database().close()
      
    
    def testMakeVrt(self):
        folder = os.path.join(test.testFolder,'1_007','ImageInt')
        files = [os.path.join(folder,f) for f in os.listdir(folder) if os.path.splitext(f)[1] == '.tif']
        vrtFile = os.path.join(folder,'test.vrt')
        if os.path.exists(vrtFile):
            os.remove(vrtFile)        
       # print(files)
        image_model.makeVrtFile(files = files, vrtFile = vrtFile)
        self.assertTrue(os.path.exists(vrtFile))
    
    
    def testLoadVrt(self):
        folder = os.path.join(test.testFolder,'1_007','ImageInt')
        files = [os.path.join(folder,f) for f in os.listdir(folder) if os.path.splitext(f)[1] == '.vrt']
        for file in files:
            image_model.loadVrt(file)



if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testImageModel)
    unittest.TextTestRunner().run(suite)
    #layer = m.loadLayer()
    #add virtual field with wkt for debugging.
    #field = QgsField('wkt', QVariant.String)
  #  layer.addExpressionField('geom_to_wkt($geometry)', field)
  
  
  