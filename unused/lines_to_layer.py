# -*- coding: utf-8 -*-
"""
Created on Wed Jun  7 08:01:16 2023

@author: Drew.Bennett

for debugging purposes. qgis cant seem to open spatialite.


"""

from PyQt5.QtSql import QSqlDatabase

from image_loader import db_functions


db = QSqlDatabase.database('image_loader')


query = db_functions.runQuery('select original_file,st_asText(line) from images_view where not line is null')
        
while query.next():
    file = query.value(0)#string
    line = query.value(1)#QVariant