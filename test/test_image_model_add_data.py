# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:14:33 2022

@author: Drew.Bennett
"""
import os

from image_loader.models.image_model import image_model,details

from image_loader import exceptions
from PyQt5.QtSql import QSqlDatabase


if __name__ == '__console__':
    from console.console import _console
    testFolder = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)

else:
    testFolder = os.path.dirname(__file__)


def testAddData(db):
    m = image_model.imageModel(db)
    file = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000003.tif'
    file2 = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000004.tif'
   
    data = [details.imageDetails(file),details.imageDetails(file2)]
    print(data)
    m.addData(data)
    print(m.rowCount())
    return m
  
if __name__ == '__main__' or __name__=='__console__':
    from PyQt5.QtWidgets import QTableView
    
    dbFile = ":memory:"
        
   # db = QSqlDatabase.addDatabase('QSPATIALITE')   #QSqlDatabase
    db = QSqlDatabase.addDatabase('QSQLITE')   #QSqlDatabase   
    
    db.setDatabaseName(dbFile)
    if not db.open():
        raise exceptions.imageLoaderError('could not create database')
        
    image_model.createTable(db)
    
    #v = QTableView()
    m = testAddData(db)
   # v.setModel(m)
    
   # v.show()
    #m.loadImages()