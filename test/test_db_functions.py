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




def testSetup():
    db = db_functions.newDb()
    db_functions.setupDb(db)



if __name__ in ['__main__','__console__']:
    testSetup()
    
    
    