    
from PyQt5.QtSql import QSqlDatabase

    
    
def getDb():
    dbFile = ":memory:"
    db = QSqlDatabase.addDatabase('QSPATIALITE')   #QSqlDatabase
    db.setDatabaseName(dbFile)
    if not db.open():
        raise exceptions.imageLoaderError('could not create database')
    return db
        