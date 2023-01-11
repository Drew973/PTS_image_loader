# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:14:33 2022
@author: Drew.Bennett
"""
from PyQt5.QtSql import QSqlDatabase

from image_loader.models.setup_database import setupDb
from image_loader.models.runs_model_spatialite.runs_model import runsModel
from image_loader.widgets.runs_view import runsView


import unittest
from image_loader import test





class testRunsModel(unittest.TestCase):
    def setUp(self):
        db = QSqlDatabase.addDatabase('QSPATIALITE','image_loader')
        db.setDatabaseName(test.dbFile)
        db.open()
        setupDb(db)
        

    def testSelect(self):
        m = runsModel(db = QSqlDatabase.database('image_loader'))
        m.select()
        #self.assertEqual(m.rowCount(),0)#more than 0 if added rows
    
    
    def tearDown(self):
        QSqlDatabase.database('image_loader').close()



 
if __name__ == '__main__' or __name__=='__console__':
    db = QSqlDatabase.addDatabase('QSPATIALITE','image_loader')
    db.setDatabaseName(r'C:\Users\drew.bennett\Documents\image_loader\test.sqlite')
    db.open()
    v = runsView()
    m = runsModel(db=db)
    v.setModel(m)
    m.select()
    v.show()
    
    
    