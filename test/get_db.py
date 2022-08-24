    
from PyQt5.QtSql import QSqlDatabase

    
class imageLoaderError(Exception):
    pass
    
    
def getDb():
    dbFile = ":memory:"
    db = QSqlDatabase.addDatabase('QSPATIALITE')   #QSqlDatabase
    db.setDatabaseName(dbFile)
    if not db.open():
        raise imageLoaderError('could not create database')
    return db
        