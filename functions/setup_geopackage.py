# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 09:19:33 2022

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlDatabase
import sqlite3
from qgis.core import QgsField,QgsFields



class imageLoaderError(Exception):
    pass


def getDb(dbFile):
    #dbFile = r'test1.db'

    #db = QSqlDatabase.addDatabase('QSPATIALITE')   #QSqlDatabase
    db = QSqlDatabase.addDatabase('QSQLITE','imageLoader')
    db.setDatabaseName(dbFile)
    if not db.open():
        raise imageLoaderError('could not create database')
    return db


import os

def createNewDb(file):
    #DELETE FILE IF EXISTS
    if os.path.isfile(file):
        os.remove(file)
        
    db = QSqlDatabase.addDatabase('QSQLITE','imageLoader')
    db.setDatabaseName(file)
    if not db.open():
        raise imageLoaderError('could not create database')    
        
    con = sqlite3.connect(db.databaseName())
    con.enable_load_extension(True)
    con.execute('SELECT load_extension("mod_spatialite")')
    con.execute("SELECT InitSpatialMetadata(1)")

    cur = con.cursor()

    q = '''
            CREATE TABLE if not exists details (
                pk integer primary key
                ,run varchar NOT NULL
                ,image_id int NOT NULL
                ,file_path VARCHAR NOT NULL
                ,name varchar
                ,groups varchar
                ,load bool default false
            )
    '''
    cur.execute(q)
    cur.execute("SELECT AddGeometryColumn('details', 'extents', 27700, 'POLYGON')")
    
    cur.execute("SELECT CreateSpatialIndex('details', 'extents');")
    
    
    con.commit()
    con.close()
    db.close()


#close connection.
#QSqlDatabase.database('imageLoader').close()

def test():
    #dbFile = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\test_db\test1.sqlite'
    dbFile = r'C:\\Users\drew.bennett\\Documents\\image_loader\\test.sqlite'

    
    createNewDb(dbFile)
    
    

test()
    
    
    
    