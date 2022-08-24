

import processing
from PyQt5.QtSql import QSqlDatabase



def createDb(file):
    uri = 'Polygon?crs=epsg:27700&field=file_path:string&field=run:string&field=image_id:int&field=name:string&field=groups:string'
    params = { 'LAYERS' : [QgsVectorLayer(uri, 'details', "memory")], 'OUTPUT' : file, 'OVERWRITE' : False, 'SAVE_METADATA' : False, 'SAVE_STYLES' : False, 'SELECTED_FEATURES_ONLY' : False }
    processing.run('native:package',params)
    db = QSqlDatabase.addDatabase('QSQLITE','imageLoader')
    db.setDatabaseName(file)
    db.close()


def loadFrames():
    db = QSqlDatabase.database('imageLoader')
    uri = db.databaseName()+'|layername=details'
    layer = iface.addVectorLayer(uri,'details', "ogr")


def test():
    dbFile = r'C:\\Users\drew.bennett\\Documents\\image_loader\\test.gpkg'
    createDb(dbFile)
    loadFrames()


if __name__=='__console__':
    test()