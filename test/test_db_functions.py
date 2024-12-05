# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 15:46:33 2023

@author: Drew.Bennett
"""


import unittest
import os
from image_loader import test

from image_loader import db_functions
from PyQt5.QtSql import QSqlDatabase
from qgis.gui import QgsVertexMarker
from qgis.utils import iface
from qgis.core import QgsPointXY
from PyQt5.QtGui import QColor



class testDbFunctions(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
       # db_functions.createDb(file = os.path.join(test.testFolder,'test.db'))
        db_functions.createDb(file = ':memory:')

        hideMarkers()
        
    def setUp(self):
        pass        

    @classmethod
    def tearDownClass(cls):
        QSqlDatabase.database('image_loader').close()
    
    def testLoadGps(self):
        db_functions.loadGps(file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv'),db = QSqlDatabase.database('image_loader'))
        self.assertTrue(db_functions.hasGps())
       # return
        p1 = QgsPointXY(354447.624,321905.030)
        m1=QgsVertexMarker(iface.mapCanvas())
        m1.setCenter(p1)
        
        ch = db_functions.getChainage(run='',x=p1.x(),y=p1.y(),db = QSqlDatabase.database('image_loader'))
        print('getChainage',ch)

        p2 = db_functions.getPoint(chainage=ch,db=QSqlDatabase.database('image_loader'))
        print(p2)
        
      #  m2=QgsVertexMarker(iface.mapCanvas())
     #   m2.setColor(QColor('green'))
    #    m2.setCenter(p2)
        
        d = p1.distance(p2)
        print('distance has error of :', d)

     #   p3 = db_functions.getPoint(chainage=14052.88,offset=0,db=QSqlDatabase.database('image_loader'))
        #print('p3',p3)
    #    self.assertTrue(p3.distance(QgsPointXY())>1)#valid point ie not 0,0

def hideMarkers():
    for item in iface.mapCanvas().scene().items():
        if issubclass(type(item), QgsVertexMarker):
            iface.mapCanvas().scene().removeItem(item)


if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testDbFunctions)
    unittest.TextTestRunner().run(suite)
    