# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 10:55:03 2023

@author: Drew.Bennett
"""


import unittest
from image_loader import test,downloads,db_functions
from PyQt5.QtWidgets import QProgressDialog


class testDownloadDistresses(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        db_functions.setFile(test.dbFile)
       # db_functions
       


    def testDownloadCracks(self):
        #downloadCracks
        prog = QProgressDialog()
        layer = test.profileFunction(downloads.downloadCracks,args = {'progress':prog})
        self.assertGreater(layer.featureCount(), 0 , 'no features in layer')

    

    def testDownloadGps(self):
        layer = test.profileFunction(downloads.downloadGps)
        self.assertGreater(layer.featureCount(),0)
     
        
     
    def testDownloadRuts(self):
        layer = test.profileFunction(downloads.downloadRuts)
        self.assertGreater(layer.featureCount(),0)
    
    
    def testDownloadFaulting(self):
        layer = test.profileFunction(downloads.downloadFaulting)
        self.assertGreater(layer.featureCount(),0) 
    
    
    
    
if __name__ in ['__main__','__console__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testDownloadDistresses)
    unittest.TextTestRunner().run(suite)
