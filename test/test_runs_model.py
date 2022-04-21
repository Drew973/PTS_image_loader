# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:14:33 2022

@author: Drew.Bennett
"""
import os

from image_loader.image_model import image_model
from image_loader import runs_model

from image_loader import exceptions
from PyQt5.QtSql import QSqlDatabase


if __name__ == '__console__':
    from console.console import _console
    testFolder = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)

else:
    testFolder = os.path.dirname(__file__)

  
if __name__ == '__main__' or __name__=='__console__':
    from PyQt5.QtWidgets import QTableView
    from qgis.core import QgsProject
    
    dbFile = ":memory:"
        
    db = QSqlDatabase.addDatabase('QSPATIALITE')   #QSqlDatabase
    db.setDatabaseName(dbFile)
    if not db.open():
        raise exceptions.imageLoaderError('could not create database')
        
        
    image_model.createTable(db)
    runs_model.createTable(db)
    
    rm = runs_model.runsModel(db)
    #rm.updateTable()
    rm.selectAll()
    v = QTableView()
    v.setModel(rm)
    v.show()
    #m.loadImages()