# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader import test
#import cProfile
from image_loader.gps_model_3 import gpsModel
#import cProfile
from qgis.core import QgsPointXY
import numpy as np



class testGpsModel(unittest.TestCase):
    
  #  @classmethod
   # def setUpClass(cls):
   #     db_functions.createDb(file = os.path.join(test.testFolder,'test.db'))
    #   # db_functions.createDb()
   

   # @classmethod
   # def tearDownClass(cls):
    #    QSqlDatabase.database('image_loader').close()    
        
    
    def setUp(self):
        self.model = gpsModel()
        self.model.clear()
        file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv')
        self.model.loadFile(file)       


    def estOriginalLine(self):
        line = self.model.originalLine(100,500)
        self.assertTrue(line.isGeosValid())
        

        
    def estGetFrame(self):
        f = self.model.getFrame(point = QgsPointXY(354503.073,322384.628))
        self.assertEqual(f,455)
        
        
    def estGcps(self):
        r = self.model.gcps(10)
        print('gcps',r)
        
        
    def testSetCorrections(self):
        self.model.setCorrections(None)
        
        
    def estRowCount(self):
        rc = self.model.rowCount()
        self.assertEqual(rc,15374)
        
        
    def estHasGps(self):
        self.assertTrue(self.model.hasGps())
        
        
    def estOriginalPoints(self):
        mo = np.array([(10,0),(20,10),(30,15)])
        p = self.model.originalPoints(mo)
        print('testOriginalPoints',p)
        
    
    def estMo(self):
        points = [
        QgsPointXY(354559.149,322010.817),
        QgsPointXY(354562.608,322012.819),
        QgsPointXY(354575.205,322011.691),
        QgsPointXY(354582.341,321997.747)
        ]
        r = self.model.mo(points,corrected=True)
        print('mo',r)
        
        
    def estPoint(self):
        mo = np.array([(0,0),(10,10),(20,5)])
       # p = self.model.point(mo)
        p = self.model.point(mo)
        print('testPoint',p)
        
        
   # def tearDown(self):
        #self.model.release()
        
        
    def estPointToFrame(self):
        p = QgsPointXY(354457.671,321926.706)
        frame = self.model.pointToFrame(p)
        self.assertEqual(frame,2708)
        pt = self.model.frameToPoint(frame)
   #     print('frameToPoint',pt)
        self.assertTrue(p.distance(pt)<10)


    def estFPLToPoint(self):
        p = self.model.FPLToPoint(1,0,0)
        print('FPLToPoint',p)


    def estPointToPixelLine(self):
        r = self.model.pointToPixelLine(frame = 2706,point = QgsPointXY(354452.430,321916.232))
        print(r)

if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testGpsModel)
    unittest.TextTestRunner().run(suite)
