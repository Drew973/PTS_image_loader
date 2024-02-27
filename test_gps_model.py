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

    @unittest.skip
    def testOriginalLine(self):
        line = self.model.originalLine(100,500)
        self.assertTrue(line.isGeosValid())
        
        
    def estGcps(self):
        r = self.model.gcps(10)
        print('gcps',r)
        
        
    @unittest.skip        
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
        
        
    @unittest.skip        
    def testPoint(self):
        mo = np.array([(0,0),(10,10),(20,5)])
       # p = self.model.point(mo)
        p = self.model.point(mo)
        print('testPoint',p)
        
        
   # def tearDown(self):
        #self.model.release()
        
        
    def testPointToFrame(self):
        p = QgsPointXY(354457.671,321926.706)
        frame = self.model.pointToFrame(p)
        self.assertEqual(frame,2708)
        pt = self.model.frameToPoint(frame)
   #     print('frameToPoint',pt)
        self.assertTrue(p.distance(pt)<10)


    #@unittest.skip
    def testFPLToPoint(self):
        frame = 2706
        p = QgsPointXY(354451.939,321913.856)
        pixel,line = self.model.pointToPixelLine(frame = frame,point = p)
        print('pixel',pixel,'line',line)
        p2 = self.model.FPLToPoint(frame,pixel,line)
        self.assertTrue(p.distance(p2) < 0.1,'point->FPL->point too far apart')
        

    @unittest.skip
    def testGetTransform(self):
        m = 13534
        t = self.model.getTransform(m) 
        print('getTransform',t)


if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testGpsModel)
    unittest.TextTestRunner().run(suite)
